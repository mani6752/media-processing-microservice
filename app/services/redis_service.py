import redis
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def set_job_status(job_id: str, status: str, extra: dict | None = None):
    data = {"status": status}
    if extra:
        data.update(extra)
    redis_client.hset(f"job:{job_id}", mapping=data)


def get_job_status(job_id: str) -> dict | None:
    data = redis_client.hgetall(f"job:{job_id}")
    return data if data else None