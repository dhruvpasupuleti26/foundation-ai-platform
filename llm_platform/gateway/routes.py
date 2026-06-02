"""FastAPI routers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from llm_platform.bootstrap import PlatformApplication
from llm_platform.gateway.dependencies import get_application
from llm_platform.schemas.gateway import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    DeploymentResponse,
    ModelDeployRequest,
    ModelRegisterRequest,
    ModelResponse,
    ModelsResponse,
    ModelUnloadRequest,
)
from llm_platform.utils.errors import NotFoundError, PlatformError, RoutingError, ValidationError


router = APIRouter()


def _translate_error(error: PlatformError) -> HTTPException:
    if isinstance(error, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, (RoutingError, ValidationError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.post("/chat/completions", response_model=ChatCompletionResponse)
def create_chat_completion(
    payload: ChatCompletionRequest,
    application: PlatformApplication = Depends(get_application),
) -> ChatCompletionResponse:
    try:
        return application.chat_service.create_completion(payload)
    except PlatformError as error:
        raise _translate_error(error) from error


@router.post("/models/register", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def register_model(
    payload: ModelRegisterRequest,
    application: PlatformApplication = Depends(get_application),
) -> ModelResponse:
    try:
        model = application.model_management_service.register_model(payload)
    except PlatformError as error:
        raise _translate_error(error) from error
    return ModelResponse(model=model)


@router.post("/models/deploy", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
def deploy_model(
    payload: ModelDeployRequest,
    application: PlatformApplication = Depends(get_application),
) -> DeploymentResponse:
    try:
        deployment = application.model_management_service.deploy_model(payload)
    except PlatformError as error:
        raise _translate_error(error) from error
    return DeploymentResponse(deployment=deployment)


@router.post("/models/unload", response_model=DeploymentResponse)
def unload_model(
    payload: ModelUnloadRequest,
    application: PlatformApplication = Depends(get_application),
) -> DeploymentResponse:
    try:
        deployment = application.model_management_service.unload_model(payload.deployment_id)
    except PlatformError as error:
        raise _translate_error(error) from error
    return DeploymentResponse(deployment=deployment)


@router.get("/models", response_model=ModelsResponse)
def list_models(application: PlatformApplication = Depends(get_application)) -> ModelsResponse:
    return ModelsResponse(models=application.model_management_service.list_models())


@router.get("/models/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: str,
    application: PlatformApplication = Depends(get_application),
) -> ModelResponse:
    try:
        model = application.model_management_service.get_model(model_id)
    except PlatformError as error:
        raise _translate_error(error) from error
    return ModelResponse(model=model)


@router.get("/health")
def get_health(application: PlatformApplication = Depends(get_application)) -> dict[str, object]:
    return application.health_service.health()


@router.get("/metrics")
def get_metrics(application: PlatformApplication = Depends(get_application)) -> dict[str, object]:
    return application.telemetry_provider.snapshot().model_dump()
