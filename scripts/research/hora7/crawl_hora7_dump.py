import asyncio, json
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup
import re

async def fetch_page():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        return result.html

async def main():
    html = await fetch_page()
    soup = BeautifulSoup(html, "html.parser")
    # Extract all visible text blocks
    blocks = []
    for el in soup.find_all(['h1','h2','h3','p','div','span','button','label']):
        txt = el.get_text(strip=True)
        if txt and len(txt) > 1:
            blocks.append(txt)
    # Save to file
    output = Path(__file__).resolve().parent / "artifacts" / "hora7_text_dump.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for b in blocks:
            f.write(b + "\n")
    print("dumped", len(blocks), "blocks")

asyncio.run(main())
