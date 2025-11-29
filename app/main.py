from fastapi import FastAPI
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
from .scheduler import start_scheduler
from .models import Video
from .routers import videos  
from sqlalchemy import select

app = FastAPI(title="Echo Shield MVP")

@app.on_event("startup")
def on_startup():
    with engine.begin() as conn:
        with open("/app/migrations/0001_init.sql", "r", encoding="utf-8") as f:
            conn.exec_driver_sql(f.read())
    start_scheduler()

@app.get("/health")
def health():
    return {"ok": True}

# 加入 router
app.include_router(videos.router)
