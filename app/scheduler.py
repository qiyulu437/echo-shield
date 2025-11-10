# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .db import SessionLocal
from .connectors.youtube import YouTubeConnector
# from .connectors.tiktok import TikTokConnector   # 先注释
from .services.ingest import upsert_video
from .config import settings
import logging

log = logging.getLogger(__name__)

def crawl_job():
    db: Session = SessionLocal()
    try:
        yt = YouTubeConnector(region=settings.YOUTUBE_COUNTRY)
        for item in yt.fetch_trending():
            v = upsert_video(db, item)
            log.info("YOUTUBE saved %s", v.id)

        # 先禁用，避免 Playwright 未安装导致报错
        # tt = TikTokConnector()
        # for item in tt.fetch_trending():
        #     v = upsert_video(db, item)
        #     log.info("TIKTOK saved %s", v.id)
    finally:
        db.close()

def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(crawl_job, "interval", minutes=settings.CRAWL_INTERVAL_MIN, id="crawl")
    sched.start()
