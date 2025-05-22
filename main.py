from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger
from uvicorn import run as uvicorn_run
from config import Settings
from routers.messages import router as messages_router
from routers.classification import router as classification_router
from routers.transactions import router as transactions_router
from routers.system import router as system_router
from exceptions import AppError
import logging

settings = Settings()

logger = logging.getLogger("app")
handler = logging.StreamHandler()
fmt = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI()

# Add API test endpoints


@app.get("/api/valid-endpoint")
async def api_valid_endpoint():
    return {"message": "OK"}


@app.post("/api/endpoint")
async def api_generic_endpoint(data: dict = Body(...)):
    # Reject empty payload
    if not data:
        raise HTTPException(status_code=400, detail={})
    return {"received": data}


# Root and About endpoints


@app.get("/", response_model=dict)
async def home():
    return {"message": "Hello"}


@app.get("/about", response_model=dict)
async def about():
    return {"message": "This is the about page."}


@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except AppError as ae:
        return JSONResponse(status_code=ae.status_code, content=ae.detail)
    except Exception:
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={
                "code": "internal_error",
                "message": "An unexpected error occurred",
            },
        )


# Include routers from app/routers

app.include_router(messages_router)
app.include_router(classification_router)
app.include_router(transactions_router)
app.include_router(system_router)

if __name__ == "__main__":
    uvicorn_run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
