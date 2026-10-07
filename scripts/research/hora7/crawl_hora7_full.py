import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        md = result.markdown
        # print first part with sections
        print(md[:12000])

asyncio.run(main())
