"""Chat request orchestration.

This module contains the application service responsible for request routing,
lightweight lifecycle updates, model-server invocation, and telemetry emission.
The service intentionally avoids transport and persistence details so it can be
tested in isolation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from llm_platform.interfaces.lifecycle import ILifecycleManager
from llm_platform.interfaces.model_server import IModelServer
from llm_platform.interfaces.registry import IRegistry
from llm_platform.interfaces.router import IRouter
from llm_platform.interfaces.telemetry import ITelemetryProvider
from llm_platform.schemas.gateway import ChatCompletionRequest, ChatCompletionResponse
from llm_platform.schemas.routing import RouteRequest
from llm_platform.schemas.telemetry import TelemetryEvent
from llm_platform.utils.errors import NotFoundError


class ChatService:
    def __init__(
        self,
        registry: IRegistry,
        router: IRouter,
        lifecycle_manager: ILifecycleManager,
        telemetry_provider: ITelemetryProvider,
        model_server: IModelServer,
        compatibility_checker: ICompatibilityChecker | None = None,
        model_cache_dir: str = "./data/model-cache",
    ) -> None:
        self._registry = registry
        self._router = router
        self._lifecycle_manager = lifecycle_manager
        self._telemetry_provider = telemetry_provider
        self._model_server = model_server
        self._compatibility_checker = compatibility_checker
        self._model_cache_dir = model_cache_dir

    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Asynchronously handles the entire chat request workflow."""
        started = perf_counter()
        
        # 1. Resolve or Onboard Model
        models = self._registry.list_models()
        model_record = None
        for m in models:
            if m.id == request.model or m.name == request.model:
                model_record = m
                break
                
        if not model_record:
            password = request.password or request.metadata.get("password")
            if password == "dhruv":
                hf_repo = request.huggingface_id or request.model
                if not hf_repo:
                    raise NotFoundError("Hugging Face repository ID must be provided for onboarding.")
                model_record = await self.onboard_model(hf_repo)
                models = self._registry.list_models()
            else:
                raise NotFoundError(f"Requested model was not found in registry: {request.model}")

        # 2. Check and Deploy Container if not ready
        deployments = self._registry.list_deployments()
        deployment_record = None
        for d in deployments:
            if d.model_id == model_record.id:
                deployment_record = d
                break
                
        from llm_platform.schemas.enums import DeploymentStatus
        if not deployment_record or deployment_record.status != DeploymentStatus.READY:
            deployment_record = await self.deploy_vllm_container(model_record, deployment_record)
            deployments = self._registry.list_deployments()

        # 3. Dynamic Router and Text Generation
        lifecycle_records = [
            record 
            for record in (self._registry.get_lifecycle(d.deployment_id) for d in deployments) 
            if record
        ]
        
        route = self._router.route(
            RouteRequest(
                capability=request.capability,
                preferred_model_id=model_record.id,
                metadata=request.metadata,
            ),
            models=models,
            deployments=deployments,
            lifecycle_records=lifecycle_records,
        )
        
        deployment = self._registry.get_deployment(route.deployment_id)
        model = self._registry.get_model(route.model_id)
        lifecycle = self._registry.get_lifecycle(route.deployment_id)
        
        if lifecycle:
            self._registry.upsert_lifecycle(self._lifecycle_manager.touch(lifecycle))
            
        # Call generate (supports both sync and async engine clients)
        import inspect
        from fastapi.concurrency import run_in_threadpool
        if inspect.iscoroutinefunction(self._model_server.generate):
            message = await self._model_server.generate(deployment, request)
        else:
            message = await run_in_threadpool(self._model_server.generate, deployment, request)
            
        latency_ms = (perf_counter() - started) * 1000.0
        self._telemetry_provider.emit(
            TelemetryEvent(
                request_id=request.request_id,
                deployment_id=route.deployment_id,
                model_name=model.name,
                latency_ms=latency_ms,
                timestamp=datetime.now(timezone.utc),
                metadata={"capability": str(request.capability)},
            )
        )
        
        return ChatCompletionResponse(
            request_id=request.request_id,
            status="accepted",
            route=route,
            message=message,
        )

    async def onboard_model(self, hf_repo: str) -> 'ModelRecord':
        from llm_platform.utils.errors import ValidationError
        if not self._compatibility_checker:
            raise ValidationError("Compatibility checker is not configured on ChatService.")
            
        report = self._compatibility_checker.inspect_huggingface_repo(hf_repo)
        if report.recommended_backend not in ["vllm", "huggingface-transformers"]:
            raise ValidationError(
                f"Model {hf_repo} is not compatible with the platform. Recommended backend: {report.recommended_backend}"
            )
            
        # Download weights asynchronously in thread pool
        from huggingface_hub import snapshot_download
        from fastapi.concurrency import run_in_threadpool
        await run_in_threadpool(
            snapshot_download,
            repo_id=hf_repo,
            cache_dir=self._model_cache_dir
        )
        
        family = "generic"
        if report.architecture:
            arch_lower = report.architecture.lower()
            if "qwen" in arch_lower:
                family = "qwen"
            elif "llama" in arch_lower:
                family = "llama"
            elif "mistral" in arch_lower:
                family = "mistral"
            elif "deepseek" in arch_lower:
                family = "deepseek"
                
        # Register Model
        from llm_platform.schemas.registry import ModelRegistrationRequest
        registration_request = ModelRegistrationRequest(
            name=hf_repo,
            version="1.0",
            family=family,
            engine="vllm",
            capabilities=["chat"],
            memory_requirement_gb=int(report.estimated_gpu_memory_gb or 16),
            ownership="user",
            metadata={
                "architecture": report.architecture or "unknown",
                "estimated_gpu_memory_gb": report.estimated_gpu_memory_gb or 0.0,
            }
        )
        model_record = self._registry.register_model(registration_request)
        
        # Register deployment as PENDING
        from llm_platform.schemas.registry import DeploymentRecord
        from llm_platform.schemas.enums import DeploymentStatus
        import uuid
        
        deployment_record = DeploymentRecord(
            deployment_id=str(uuid.uuid4()),
            model_id=model_record.id,
            endpoint="http://localhost:pending",
            engine="vllm",
            status=DeploymentStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            metadata={}
        )
        self._registry.update_deployment(deployment_record)
        
        return model_record

    async def deploy_vllm_container(
        self, 
        model_record: 'ModelRecord', 
        existing_deployment: 'DeploymentRecord' | None
    ) -> 'DeploymentRecord':
        import socket
        import docker
        from fastapi.concurrency import run_in_threadpool
        from pathlib import Path
        from llm_platform.schemas.enums import DeploymentStatus
        from llm_platform.schemas.registry import DeploymentRecord
        import uuid
        
        # Find free port starting at 8002
        port = 8002
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    break
                except OSError:
                    port += 1
                    
        sanitized_name = model_record.name.replace("/", "-").replace(".", "-").replace(":", "-").lower()
        container_name = f"vllm-{sanitized_name}"
        
        def run_docker():
            client = docker.from_env()
            try:
                existing = client.containers.get(container_name)
                existing.remove(force=True)
            except docker.errors.NotFound:
                pass
                
            device_request = docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
            host_path = str(Path(self._model_cache_dir).resolve())
            container_path = "/root/.cache/huggingface"
            
            return client.containers.run(
                image="vllm/vllm-openai:latest",
                command=f"--model {model_record.name} --port {port} --host 0.0.0.0",
                name=container_name,
                detach=True,
                network_mode="host",
                volumes={
                    host_path: {
                        'bind': container_path,
                        'mode': 'rw'
                    }
                },
                device_requests=[device_request]
            )
            
        await run_in_threadpool(run_docker)
        
        # Poll readiness health check
        import httpx
        import asyncio
        url = f"http://localhost:{port}/v1/models"
        ready = False
        async with httpx.AsyncClient() as client:
            for _ in range(60):
                try:
                    response = await client.get(url, timeout=2.0)
                    if response.status_code == 200:
                        ready = True
                        break
                except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
                    pass
                await asyncio.sleep(5)
                
        if not ready:
            raise RuntimeError(f"vLLM container for {model_record.name} failed to become healthy on port {port}")
            
        endpoint = f"http://localhost:{port}"
        
        if existing_deployment:
            existing_deployment.endpoint = endpoint
            existing_deployment.status = DeploymentStatus.READY
            existing_deployment.metadata["port"] = port
            existing_deployment.metadata["container_name"] = container_name
            deployment_record = self._registry.update_deployment(existing_deployment)
        else:
            deployment_record = DeploymentRecord(
                deployment_id=str(uuid.uuid4()),
                model_id=model_record.id,
                endpoint=endpoint,
                engine="vllm",
                status=DeploymentStatus.READY,
                created_at=datetime.now(timezone.utc),
                metadata={"port": port, "container_name": container_name}
            )
            self._registry.update_deployment(deployment_record)
            
        return deployment_record
