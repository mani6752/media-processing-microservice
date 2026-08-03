import time
import os
import tempfile

from app.celery_app import celery_app
from app.services.redis_service import set_job_status

from app.services.s3_service import (
    download_file,
    download_file_to_path,
    upload_file,
    upload_local_file,
)

from app.services.image_service import (
    resize_image,
    create_thumbnail,
)

from app.services.video_processor import VideoProcessor


@celery_app.task(
    name="process_media_job",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_media_job(self, job_id: str, object_key: str):
    try:
        set_job_status(job_id, "processing")

        # Image processing
        if object_key.lower().endswith((".jpg", ".jpeg", ".png")):

            original_bytes = download_file(object_key)

            resized_bytes = resize_image(original_bytes)
            thumbnail_bytes = create_thumbnail(original_bytes)

            resized_key = object_key.replace("uploads/", "processed/")
            thumbnail_key = object_key.replace("uploads/", "thumbnails/")

            upload_file(resized_key, resized_bytes)
            upload_file(thumbnail_key, thumbnail_bytes)

            result = {
                "resized_key": resized_key,
                "thumbnail_key": thumbnail_key,
            }

        else:
            # Video processing will be added next
            result = {
                "message": "Video processing coming next"
            }

        set_job_status(job_id, "completed", result)

        return {
            "job_id": job_id,
            "status": "completed",
        }

    except Exception as exc:
        set_job_status(job_id, "failed", {"error": str(exc)})
        raise self.retry(exc=exc)