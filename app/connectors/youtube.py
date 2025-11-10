# app/connectors/youtube.py
import os
import requests
import yt_dlp
from .base import Connector, RawVideo

API_URL = "https://www.googleapis.com/youtube/v3/videos"

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": False,
    "nocheckcertificate": True,
}

def _download_thumb(url: str | None) -> bytes:
    if not url:
        return b""
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.content

class YouTubeConnector(Connector):
    def __init__(self, region="US"):
        self.region = region
        self.api_key = os.getenv("YOUTUBE_API_KEY")

    def fetch_trending(self):
        # 1) 优先 Data API：chart=mostPopular
        if self.api_key:
            params = {
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": self.region,
                "maxResults": 50,
                "key": self.api_key,
            }
            resp = requests.get(API_URL, params=params, timeout=25)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("items", []):
                vid = item["id"]
                sn = item["snippet"]
                st = item.get("statistics", {})
                thumb_url = (
                    sn.get("thumbnails", {}).get("medium", {},).get("url")
                    or sn.get("thumbnails", {}).get("default", {},).get("url")
                )
                yield RawVideo(
                    platform="youtube",
                    platform_video_id=vid,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    title=sn.get("title"),
                    author=sn.get("channelTitle"),
                    published_at=sn.get("publishedAt"),
                    thumb_bytes=_download_thumb(thumb_url),
                    engage_views=int(st.get("viewCount", 0) or 0),
                    engage_likes=int(st.get("likeCount", 0) or 0),
                    engage_comments=int(st.get("commentCount", 0) or 0),
                    engage_shares=0,
                )
            return

        # 2) 无 API Key：用 yt-dlp 搜索近似热门内容作为兜底
        # 避开 /feed/trending，使用 ytsearch 查询
        query = "ytsearch50 viral OR news OR AI"
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(query, download=False)
        for e in info.get("entries", []) or []:
            if not e:
                continue
            vid = e.get("id")
            yield RawVideo(
                platform="youtube",
                platform_video_id=vid,
                url=f"https://www.youtube.com/watch?v={vid}",
                title=e.get("title"),
                author=(e.get("uploader") or e.get("channel")),
                published_at=e.get("upload_date"),
                thumb_bytes=_download_thumb(e.get("thumbnail")),
                engage_views=e.get("view_count") or 0,
                engage_likes=e.get("like_count") or 0,
                engage_comments=0,
                engage_shares=0,
            )
