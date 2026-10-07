import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup

async def main():
    browser_cfg = BrowserConfig(headless=True, verbose=False)
    run_cfg = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        soup = BeautifulSoup(result.html, "html.parser")
        # Find all text nodes
        texts = []
        for tag in soup.find_all(['button','a','label','input']):
            t = tag.get_text(strip=True)
            if t:
                texts.append(t)
        # Find navigation or menu items
        print("--- UI TEXTS ---")
        for t in texts[:200]:
            print("-", t)
        # Extract buttons
        buttons = [b.get_text(strip=True) for b in soup.find_all('button')]
        print("\n--- BUTTONS ---")
        for b in buttons:
            print("-", b)

asyncio.run(main())
