import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="domcontentloaded", delay_before_return_html=2.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        print("status:", result.success)
        print("url:", result.url)
        # markdown summary
        print("\n--- MARKDOWN START ---")
        print(result.markdown[:8000])
        print("--- MARKDOWN END ---")
        # maybe html snippet
        if result.html:
            print("\nHTML length:", len(result.html))
        # structured data if any
        if result.extracted_content:
            print("\nExtracted:", result.extracted_content)

asyncio.run(main())
