import boto3
from botocore.client import Config

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        endpoint_url=settings.aws_s3_endpoint,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def upload_bytes(key: str, data: bytes, content_type: str = "text/csv") -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.aws_bucket_name,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key


