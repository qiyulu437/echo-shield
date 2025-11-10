# app/services/ingest.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Video
from ..storage import put_bytes
from ..hashing import phash_from_bytes
from datetime import datetime

def upsert_video(db: Session, raw):
    existing = db.execute(
        select(Video).where(
            Video.platform == raw["platform"],
            Video.platform_video_id == raw["platform_video_id"])
    ).scalar_one_or_none()
    if existing:
        return existing

    thumb_uri, phash = None, None
    tb = raw.get("thumb_bytes") or b""
    if tb:
        phash = phash_from_bytes(tb)
        thumb_uri = put_bytes(tb, "thumbs", f'{raw["platform"]}_{raw["platform_video_id"]}.jpg')

    v = Video(
        platform=raw["platform"],
        platform_video_id=raw["platform_video_id"],
        url=raw["url"],
        title=raw.get("title"),
        author=raw.get("author"),
        published_at=None,
        collected_at=datetime.utcnow(),
        thumb_s3_uri=thumb_uri,
        engage_views=raw.get("engage_views", 0),
        engage_likes=raw.get("engage_likes", 0),
        engage_comments=raw.get("engage_comments", 0),
        engage_shares=raw.get("engage_shares", 0),
        phash=phash,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v
