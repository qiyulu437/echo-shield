from typing import Iterable, TypedDict, Optional

class RawVideo(TypedDict, total=False):
    platform: str
    platform_video_id: str
    url: str
    title: str
    author: str
    published_at: Optional[str]
    thumb_bytes: bytes
    engage_views: int
    engage_likes: int
    engage_comments: int
    engage_shares: int

class Connector:
    def fetch_trending(self) -> Iterable[RawVideo]:
        raise NotImplementedError
