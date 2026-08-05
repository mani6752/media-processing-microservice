from fastapi import FastAPI
from fastapi.responses import Response

from app.routers import upload
from app.services.metrics_service import collect_metrics
from prometheus_client import CONTENT_TYPE_LATEST

app = FastAPI(
    title="Media Processing Microservice",
    description="Handles async media upload processing (resize, compress, watermark).",
    version="0.1.0",
)
app.include_router(upload.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "media-processing-microservice"}


@app.get("/metrics")
def metrics():
    return Response(content=collect_metrics(), media_type=CONTENT_TYPE_LATEST)