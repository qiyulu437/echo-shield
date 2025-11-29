# app/services/ingest.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from .ai_score import score_from_meta
from app.models import Video
from ..storage import put_bytes
from ..hashing import phash_from_bytes


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

    score, hits_cnt, hit_list = score_from_meta(
        title=raw.get("title"),
        description=raw.get("description"),
        tags=raw.get("tags"),
        duration_seconds=raw.get("duration_seconds"),
        category_id=raw.get("category_id"),
        channel_title=raw.get("author"),
        comments=raw.get("comments"),  # 目前可以先传 None
    )
    
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
        ai_meta_score = score,
        ai_meta_hits = hits_cnt,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v
