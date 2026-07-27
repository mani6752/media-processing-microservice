from fastapi import FastAPI
from app.routers import upload

app = FastAPI(
    title="Media Processing Microservice",
    description="Handles async media upload processing (resize, compress, watermark).",
    version="0.1.0",
)

app.include_router(upload.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "media-processing-microservice"}