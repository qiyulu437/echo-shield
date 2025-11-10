# app/storage.py
from minio import Minio
from .config import settings
from datetime import datetime
from io import BytesIO

client = Minio(
    settings.S3_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=settings.S3_SECURE,
)

def ensure_bucket():
    if not client.bucket_exists(settings.S3_BUCKET):
        client.make_bucket(settings.S3_BUCKET)

def put_bytes(data: bytes, key_prefix: str, filename: str) -> str:
    ensure_bucket()
    key = f"{key_prefix}/{datetime.utcnow().strftime('%Y%m%d')}/{filename}"
    bio = BytesIO(data)
    client.put_object(
        settings.S3_BUCKET,
        key,
        data=bio,                      # 传入文件流
        length=len(data),              # 必须指定长度
        content_type="image/jpeg",     # 缩略图是 jpg，按需调整
    )
    return f"s3://{settings.S3_BUCKET}/{key}"
