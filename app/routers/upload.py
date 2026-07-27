import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.s3_service import generate_presigned_upload_url
from app.services.redis_service import set_job_status, get_job_status

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadRequest(BaseModel):
    filename: str


class UploadResponse(BaseModel):
    upload_url: str
    object_key: str
    job_id: str


@router.post("/request-url", response_model=UploadResponse)
def request_upload_url(payload: UploadRequest):
    job_id = str(uuid.uuid4())
    object_key = f"uploads/{payload.filename}"
    url = generate_presigned_upload_url(object_key)

    set_job_status(job_id, "pending", {"object_key": object_key, "filename": payload.filename})

    return UploadResponse(upload_url=url, object_key=object_key, job_id=job_id)


@router.get("/status/{job_id}")
def check_job_status(job_id: str):
    status = get_job_status(job_id)
    if not status:
        return {"error": "job not found"}
    return status
