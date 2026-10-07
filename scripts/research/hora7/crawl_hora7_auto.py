import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=5.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        # Try to get page with form filled? For now just dump
        html = result.html
        # Save
        output = Path(__file__).resolve().parent / "artifacts" / "hora7_automation.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output,"w",encoding="utf-8") as f:
            f.write(html)
        print("saved html len", len(html))
        # Print some snippet
        print(result.markdown[:2000])

asyncio.run(main())
