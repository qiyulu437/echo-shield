import asyncio
from playwright.async_api import async_playwright
from .base import Connector, RawVideo

# 说明：TikTok 官方 API 不开放。这里用 Playwright 打开 trending/discover 页，
# 提取卡片中的视频链接/标题/作者/封面。若地区/反爬变更，需要适当调整选择器。

TT_DISCOVER = "https://www.tiktok.com/explore"

class TikTokConnector(Connector):
    def __init__(self, headless=True):
        self.headless = headless

    def fetch_trending(self):
        return asyncio.run(self._fetch())

    async def _fetch(self):
        out: list[RawVideo] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            ctx = await browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ))
            page = await ctx.new_page()
            await page.goto(TT_DISCOVER, wait_until="domcontentloaded")
            # 简单滚动加载
            for _ in range(3):
                await page.mouse.wheel(0, 2000)
                await page.wait_for_timeout(800)

            cards = page.locator('a[href*="/video/"] >> nth=0').locator("..")
            elements = await page.locator('a[href*="/video/"]').all()
            for a in elements[:50]:
                href = await a.get_attribute("href")
                if not href:
                    continue
                # 取 video_id
                vid = href.split("/video/")[-1].split("?")[0]
                thumb = await a.locator("img").first.get_attribute("src")
                title = await a.get_attribute("title")
                out.append(RawVideo(
                    platform="tiktok",
                    platform_video_id=vid,
                    url=f"https://www.tiktok.com{href}" if href.startswith("/") else href,
                    title=title or "",
                    author="",  # 可进一步解析作者元素
                    published_at=None,
                    thumb_bytes=await _download_bytes(ctx, thumb) if thumb else b"",
                    engage_views=0, engage_likes=0, engage_comments=0, engage_shares=0
                ))
            await browser.close()
        return out

async def _download_bytes(ctx, url: str) -> bytes:
    if not url:
        return b""
    r = await ctx.request.get(url, timeout=15000)
    if r.ok:
        return await r.body()
    return b""
