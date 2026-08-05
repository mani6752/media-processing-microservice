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

from app.services.metrics_service import (
    TASKS_SUCCEEDED,
    TASKS_FAILED,
    TASK_DURATION,
)


VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv")


@celery_app.task(
    name="process_media_job",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_media_job(self, job_id: str, object_key: str):
    start_time = time.monotonic()

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

        elif object_key.lower().endswith(VIDEO_EXTENSIONS):

            with tempfile.TemporaryDirectory() as tmp_dir:
                input_ext = os.path.splitext(object_key)[1]
                input_path = os.path.join(tmp_dir, f"input{input_ext}")
                thumbnail_path = os.path.join(tmp_dir, "thumbnail.jpg")
                output_path = os.path.join(tmp_dir, "output.mp4")

                download_file_to_path(object_key, input_path)

                VideoProcessor.create_thumbnail(input_path, thumbnail_path)
                VideoProcessor.convert_to_mp4(input_path, output_path)

                thumbnail_key = object_key.replace("uploads/", "thumbnails/")
                thumbnail_key = os.path.splitext(thumbnail_key)[0] + ".jpg"

                processed_key = object_key.replace("uploads/", "processed/")
                processed_key = os.path.splitext(processed_key)[0] + ".mp4"

                upload_local_file(thumbnail_key, thumbnail_path)
                upload_local_file(processed_key, output_path)

                result = {
                    "thumbnail_key": thumbnail_key,
                    "processed_key": processed_key,
                }

        else:
            result = {
                "message": f"Unsupported file type: {object_key}"
            }

        set_job_status(job_id, "completed", result)

        TASKS_SUCCEEDED.inc()
        TASK_DURATION.observe(time.monotonic() - start_time)

        return {
            "job_id": job_id,
            "status": "completed",
        }

    except Exception as exc:
        set_job_status(job_id, "failed", {"error": str(exc)})

        TASKS_FAILED.inc()
        TASK_DURATION.observe(time.monotonic() - start_time)

        raise self.retry(exc=exc)
    