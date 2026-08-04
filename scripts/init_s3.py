"""
Ensures the S3 bucket exists before the app starts.
Safe to run every time — it's a no-op if the bucket already exists.
Only relevant when using mock S3 (moto); real AWS buckets should be
created via infrastructure-as-code, not app startup code.
"""
import time
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from app.config import settings


def wait_for_mock_s3_and_create_bucket():
    if not settings.use_mock_s3:
        print("USE_MOCK_S3 is False — skipping mock bucket creation.")
        return

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )

    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            existing = s3.list_buckets()
            bucket_names = [b["Name"] for b in existing.get("Buckets", [])]

            if settings.s3_bucket_name in bucket_names:
                print(f"Bucket '{settings.s3_bucket_name}' already exists.")
            else:
                s3.create_bucket(Bucket=settings.s3_bucket_name)
                print(f"Bucket '{settings.s3_bucket_name}' created.")
            return

        except EndpointConnectionError:
            print(f"Mock S3 not ready yet (attempt {attempt}/{max_attempts}), retrying...")
            time.sleep(2)
        except ClientError as e:
            print(f"Unexpected S3 error: {e}")
            raise

    raise RuntimeError("Mock S3 never became available after multiple attempts.")


if __name__ == "__main__":
    wait_for_mock_s3_and_create_bucket()
    