import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup
import re, json

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        soup = BeautifulSoup(result.html, "html.parser")
        scripts = soup.find_all("script")
        texts = []
        for s in scripts:
            if s.get("src"):
                texts.append({"src": s["src"], "inline": False})
            else:
                txt = s.get_text() or ""
                if txt.strip():
                    texts.append({"src": None, "inline": True, "len": len(txt), "preview": txt[:500]})
        # Save
        out = {
            "script_count": len(scripts),
            "scripts": texts[:200]
        }
        output = Path(__file__).resolve().parent / "artifacts" / "hora7_scripts.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(json.dumps(out, ensure_ascii=False, indent=2)[:10000])

asyncio.run(main())
