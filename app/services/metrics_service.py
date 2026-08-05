import os
import psutil
from prometheus_client import (
    Gauge,
    Counter,
    Histogram,
    CollectorRegistry,
    multiprocess,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from app.celery_app import celery_app


# --- Task-level metrics (updated from within tasks.py) ---
TASKS_SUCCEEDED = Counter(
    "media_tasks_succeeded_total",
    "Total number of media processing tasks that completed successfully",
)

TASKS_FAILED = Counter(
    "media_tasks_failed_total",
    "Total number of media processing tasks that failed",
)

TASK_DURATION = Histogram(
    "media_task_duration_seconds",
    "Time taken to process a media job, in seconds",
)


# --- System / infra metrics (computed on each /metrics scrape) ---
QUEUE_LENGTH = Gauge(
    "celery_queue_length",
    "Number of tasks currently waiting in the default Celery queue",
)

WORKER_CPU_PERCENT = Gauge(
    "celery_worker_cpu_percent",
    "CPU usage percent of the current process (worker or api, whichever scrapes this)",
)


def get_queue_length(queue_name: str = "celery") -> int:
    """
    Asks RabbitMQ (via Celery's connection) how many messages are
    currently sitting in the queue, waiting to be picked up by a worker.
    """
    try:
        with celery_app.connection_or_acquire() as conn:
            queue = conn.default_channel.queue_declare(queue=queue_name, passive=True)
            return queue.message_count
    except Exception:
        # Queue may not exist yet if nothing has been submitted — treat as 0
        return 0


def collect_metrics() -> bytes:
    """
    Refreshes the gauges with live values, then returns the full
    Prometheus-formatted metrics payload for the /metrics endpoint.
    """
    QUEUE_LENGTH.set(get_queue_length())
    WORKER_CPU_PERCENT.set(psutil.cpu_percent(interval=0.1))

    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return generate_latest(registry)

    return generate_latest()
