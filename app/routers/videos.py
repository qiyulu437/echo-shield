from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import Video

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/latest")
def latest_videos(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Video).order_by(Video.collected_at.desc()).limit(50)
        ).scalars().all()
    )
    return [
        {
            "id": str(r.id),
            "platform": r.platform,
            "platform_video_id": r.platform_video_id,
            "title": r.title,
            "url": r.url,
            "thumb": r.thumb_s3_uri,
            "phash": r.phash,
            "views": r.engage_views,
            "ai_meta_score": r.ai_meta_score,
            "ai_meta_hits": r.ai_meta_hits,
        }
        for r in rows
    ]
