from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_access_key_id: str = "testing"
    aws_secret_access_key: str = "testing"
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "media-processing-bucket"
    use_mock_s3: bool = True
    s3_endpoint_url: str = "http://127.0.0.1:5000"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
