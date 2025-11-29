# app/models/video.py
import uuid

from sqlalchemy import (
    Column,
    Text,
    DateTime,
    BigInteger,
    Float,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base 


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(Text, nullable=False)
    platform_video_id = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text)
    author = Column(Text)
    published_at = Column(DateTime)
    collected_at = Column(DateTime, nullable=False)

    thumb_s3_uri = Column(Text)

    # 先不管 sample_frames_s3_uri，后面要用再补
    # sample_frames_s3_uri = Column(ARRAY(Text))  # 如果需要再加

    engage_views = Column(BigInteger, default=0)
    engage_likes = Column(BigInteger, default=0)
    engage_comments = Column(BigInteger, default=0)
    engage_shares = Column(BigInteger, default=0)

    popularity_score = Column(Float)
    phash = Column(Text)

    ai_meta_score = Column(Float, nullable=True)
    ai_meta_hits = Column(Integer, default=0)
