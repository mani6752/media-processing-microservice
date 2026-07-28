import time
from app.celery_app import celery_app
from app.services.redis_service import set_job_status


@celery_app.task(
    name="process_media_job",
    bind=True,
    max_retries=3,
    default_retry_delay=10,  # seconds between retries
)
def process_media_job(self, job_id: str, object_key: str):
    try:
        set_job_status(job_id, "processing")

        # Simulate media processing work (we'll replace this with real
        # Pillow/FFmpeg logic in Week 3)
        time.sleep(5)

        set_job_status(job_id, "completed")
        return {"job_id": job_id, "object_key": object_key, "status": "completed"}

    except Exception as exc:
        set_job_status(job_id, "failed", {"error": str(exc)})
        raise self.retry(exc=exc)
    