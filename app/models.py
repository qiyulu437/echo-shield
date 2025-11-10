import uuid
from sqlalchemy import Column, String, Text, BigInteger, Float, ARRAY, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from .db import Base

class Video(Base):
    __tablename__ = "videos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(Text, nullable=False)
    platform_video_id = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text)
    author = Column(Text)
    published_at = Column(TIMESTAMP)
    collected_at = Column(TIMESTAMP)
    thumb_s3_uri = Column(Text)
    sample_frames_s3_uri = Column(ARRAY(Text))
    engage_views = Column(BigInteger)
    engage_likes = Column(BigInteger)
    engage_comments = Column(BigInteger)
    engage_shares = Column(BigInteger)
    popularity_score = Column(Float)
    phash = Column(String)

class Detection(Base):
    __tablename__ = "detections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True))
    provider = Column(Text)
    confidence = Column(Float)
    label = Column(Text)
    evidence_s3_uri = Column(Text)
    run_at = Column(TIMESTAMP)
