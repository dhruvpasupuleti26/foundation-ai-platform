# Dynamic vLLM Onboarding & Cache Sync - Detailed Breakdown

Here is a complete, detailed breakdown of all the major changes we built into the platform today. I have included the exact code snippets we added, along with the *why* and *how* for each feature.

---

### 1. Expanding the Gateway Payload
**File:** `llm_platform/schemas/gateway.py`

```python
class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatCompletionMessage]
    password: str | None = None
    huggingface_id: str | None = None
    # ... other standard OpenAI params
```
**Why we did it:** The original repo only accepted standard OpenAI fields (like `model` and `messages`). If a user wanted a model that didn't exist yet, there was no way to authorize them to trigger a massive 15GB download. 
**How it works:** We expanded the payload to accept a custom `password` field and a `huggingface_id`. This allows the gateway to securely intercept specific requests that demand dynamic onboarding.

---

### 2. Auto-Creating the Database on Startup
**File:** `llm_platform/bootstrap.py`

```python
            if config.database.engine.lower() == "sqlite":
                from pathlib import Path
                Path(config.database.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
                from sqlalchemy import create_engine
                from llm_platform.database.models import Base
                engine = create_engine(config.database.sqlalchemy_url)
                Base.metadata.create_all(bind=engine)
```
**Why we did it:** Originally, the platform relied on users running Alembic migration scripts (`scripts/bootstrap.py`) before starting the server. If they didn't, the database tables wouldn't exist, and the server would silently crash or throw 404s.
**How it works:** We injected SQLAlchemy's `create_all()` directly into the Uvicorn startup sequence. Now, it checks if the `data` folder exists (creating it if it doesn't), and automatically generates all necessary tables so the platform works out-of-the-box.

---

### 3. The SSD Auto-Sync Engine
**File:** `llm_platform/bootstrap.py`

```python
            cache_path = Path(getattr(config.serving, 'model_cache_dir', './data/model-cache')).expanduser().resolve()
            if cache_path.exists():
                for d in cache_path.iterdir():
                    if d.is_dir() and d.name.startswith("models--"):
                        repo_id = d.name.replace("models--", "").replace("--", "/")
                        if not any(m.name == repo_id for m in existing_models):
                            print(f"[SSD Sync] Found un-registered model on SSD: {repo_id}. Auto-registering...")
                            # ... Saves new ModelRecord and DeploymentRecord (as PENDING) into SQLite
```
**Why we did it:** If the database file is deleted, the server forgets what models you've already downloaded to your SSD. This causes the server to try and re-download models from scratch.
**How it works:** On startup, the server actively scans your `data/model-cache` directory. HuggingFace saves folders using a specific naming convention (`models--deepseek-ai--...`). The script parses these folder names back into standard HuggingFace repo IDs (e.g., `deepseek-ai/...`), checks if they exist in the database, and if not, automatically registers them so they are instantly ready to be served.

---

### 4. Dynamic Model Onboarding
**File:** `llm_platform/services/chat.py`

```python
        if not model_record:
            password = request.password or request.metadata.get("password")
            if password == "dhruv":
                hf_repo = request.huggingface_id or request.model
                model_record = await self.onboard_model(hf_repo)
            else:
                raise NotFoundError(f"Requested model was not found in registry: {request.model}")

    # Inside onboard_model():
        await run_in_threadpool(
            snapshot_download,
            repo_id=hf_repo,
            cache_dir=self._model_cache_dir
        )
```
**Why we did it:** We needed the platform to react to unknown requests intelligently rather than just blindly failing.
**How it works:** When a chat request arrives for a model not in the registry, it checks the payload for the `"dhruv"` password. If correct, it triggers `onboard_model()`. This uses the `huggingface_hub` library's `snapshot_download` to pull the raw model weights down to your SSD's cache directory in the background. If the password isn't there, it securely throws a 404.

---

### 5. vLLM Docker Orchestration & Direct Cache Mounting
**File:** `llm_platform/services/chat.py`

```python
        # Ensure the cache directory exists before mounting
        host_cache_path = Path(self._model_cache_dir).resolve()
        host_cache_path.mkdir(parents=True, exist_ok=True)
        host_path = str(host_cache_path)
        
        # Mount it exactly where the huggingface hub inside the container expects it
        container_path = "/root/.cache/huggingface/hub"
        
        client.containers.run(
            image="vllm/vllm-openai:latest",
            command=f"--model {model_record.name} --port {port} --host 0.0.0.0",
            volumes={ host_path: { 'bind': container_path, 'mode': 'rw' } },
            device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]
        )
```
**Why we did it:** Downloading weights is useless unless an inference engine can serve them. We also had the critical bug where vLLM was ignoring our downloaded weights and downloading them *again* inside the container.
**How it works:** The platform spawns an isolated vLLM Docker container dynamically. Crucially, we map our host's `data/model-cache` directory perfectly into the container's `/root/.cache/huggingface/hub` folder. This is exactly where vLLM looks by default, allowing it to instantly detect the weights we just downloaded and load them into the GPU.

---

### 6. The SQLAlchemy Metadata Fix
**File:** `llm_platform/services/chat.py`

```python
            new_metadata = dict(existing_deployment.metadata)
            new_metadata["port"] = port
            new_metadata["base_url"] = endpoint
            new_metadata["remote_model_name"] = model_record.name
            existing_deployment.metadata = new_metadata
            self._registry.update_deployment(existing_deployment)
```
**Why we did it:** Once the Docker container spun up, we needed to save its `port` and `base_url` into the database so the platform knew where to route the request. However, when we updated the dictionary directly (`existing.metadata["port"] = port`), SQLAlchemy ignored the change and saved nothing.
**How it works:** SQLAlchemy (and SQLite specifically) doesn't track deep mutations inside JSON columns. By creating an entirely new dictionary copy (`dict(...)`), adding our keys to it, and reassigning it, we trick SQLAlchemy into seeing the field as "dirty" and forcing it to save the updated connection details to the database!
