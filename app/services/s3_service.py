import os
import boto3
from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )


def ensure_bucket_exists():
    s3 = get_s3_client()
    existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if settings.s3_bucket_name not in existing_buckets:
        s3.create_bucket(Bucket=settings.s3_bucket_name)


def generate_presigned_upload_url(object_key: str, expires_in: int = 3600):
    s3 = get_s3_client()
    ensure_bucket_exists()
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": object_key},
        ExpiresIn=expires_in,
    )
    return url


def download_file(object_key: str) -> bytes:
    s3 = get_s3_client()
    response = s3.get_object(Bucket=settings.s3_bucket_name, Key=object_key)
    return response["Body"].read()


def upload_file(object_key: str, file_bytes: bytes, content_type: str = "image/jpeg"):
    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=object_key,
        Body=file_bytes,
        ContentType=content_type,
    )


def download_file_to_path(object_key: str, local_path: str):
    s3 = get_s3_client()

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    s3.download_file(
        settings.s3_bucket_name,
        object_key,
        local_path,
    )


def upload_local_file(
    object_key: str,
    local_path: str,
    content_type: str = "video/mp4",
):
    s3 = get_s3_client()

    with open(local_path, "rb") as f:
        s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Body=f,
            ContentType=content_type,
        )