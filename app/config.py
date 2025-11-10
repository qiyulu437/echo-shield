from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "echo-shield"
    S3_REGION: str = "us-east-1"
    S3_SECURE: bool = False

    CRAWL_INTERVAL_MIN: int = 5
    YOUTUBE_COUNTRY: str = "US"

settings = Settings()
