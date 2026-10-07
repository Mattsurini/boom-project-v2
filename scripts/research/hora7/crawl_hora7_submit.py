import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=5.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        # Save markdown for inspection
        output = Path(__file__).resolve().parent / "artifacts" / "hora7_result.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output,"w",encoding="utf-8") as f:
            f.write(result.markdown)
        print("saved", len(result.markdown))
        print(result.markdown[:3000])

asyncio.run(main())
