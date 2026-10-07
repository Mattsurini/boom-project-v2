import asyncio, os, re, json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from urllib.parse import urljoin

BASE = "https://hora-7-of-9-base.vercel.app"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT_DIR, exist_ok=True)

async def fetch_page():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=BASE, config=run_cfg)
        return result.html

def extract_js_urls(html):
    urls = []
    # find script src
    pattern = re.compile(r'<script[^>]+src="([^"]+)"', re.I)
    for m in pattern.finditer(html):
        src = m.group(1)
        if src.startswith("/_next/static"):
            urls.append(src)
    # dedupe keep order
    seen=set()
    uniq=[]
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq

async def download_js(urls):
    import aiohttp
    async with aiohttp.ClientSession() as session:
        for rel in urls:
            full = urljoin(BASE, rel)
            try:
                async with session.get(full, timeout=30) as resp:
                    if resp.status==200:
                        data = await resp.read()
                        fname = os.path.basename(rel)
                        path = os.path.join(OUT_DIR, fname)
                        with open(path, "wb") as f:
                            f.write(data)
                        print("downloaded", fname, len(data))
                    else:
                        print("failed", rel, resp.status)
            except Exception as e:
                print("error", rel, e)

async def main():
    html = await fetch_page()
    urls = extract_js_urls(html)
    print("found", len(urls), "js urls")
    await download_js(urls)
    # save list
    with open(os.path.join(OUT_DIR, "js_list.json"), "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)

asyncio.run(main())
