# app/storage.py
from datetime import datetime
from io import BytesIO

from minio import Minio

from .config import settings


# 处理 endpoint，把 http:// 或 https:// 去掉，交给 secure 参数控制
_endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")

# 这里所有参数都用关键字形式，避免 Minio 新版的签名问题
client = Minio(
    endpoint=_endpoint,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=settings.S3_SECURE,
)


def ensure_bucket() -> None:
    if not client.bucket_exists(bucket_name=settings.S3_BUCKET):
        client.make_bucket(bucket_name=settings.S3_BUCKET)


def put_bytes(data: bytes, key_prefix: str, filename: str) -> str:
    ensure_bucket()

    key = f"{key_prefix}/{datetime.utcnow().strftime('%Y%m%d')}/{filename}"

    bio = BytesIO(data)
    client.put_object(
        bucket_name=settings.S3_BUCKET,
        object_name=key,
        data=bio,               # MinIO 需要一个有 .read() 的流对象
        length=len(data),
        content_type="image/jpeg",
    )

    return f"s3://{settings.S3_BUCKET}/{key}"
