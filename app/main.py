from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
from .scheduler import start_scheduler
from .models import Video
from sqlalchemy import select

app = FastAPI(title="Echo Shield MVP")

@app.on_event("startup")
def on_startup():
    # 迁移（简化：直接执行 SQL 文件，也可用 Alembic）
    with engine.begin() as conn:
        with open("/app/migrations/0001_init.sql", "r", encoding="utf-8") as f:
            conn.exec_driver_sql(f.read())
    start_scheduler()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/videos/latest")
def latest(db: Session = Depends(get_db)):
    rows = db.execute(select(Video).order_by(Video.collected_at.desc()).limit(50)).scalars().all()
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
        } for r in rows
    ]
