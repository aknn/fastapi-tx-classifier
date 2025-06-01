from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from fastapi.responses import JSONResponse, Response as PrometheusResponse
from ..redis_client import get_redis
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check status",
)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"}, status_code=status.HTTP_200_OK)


@router.get(
    "/ready",
    response_model=Dict[str, bool],
    summary="Readiness probe",
)
async def ready(redis: Any = Depends(get_redis)) -> JSONResponse:
    try:
        await redis.ping()
        return JSONResponse({"ready": True}, status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(
            {"ready": False}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get(
    "/metrics",
    summary="Prometheus metrics endpoint",
)
def metrics() -> PrometheusResponse:
    data = generate_latest()
    return PrometheusResponse(content=data, media_type=CONTENT_TYPE_LATEST)
