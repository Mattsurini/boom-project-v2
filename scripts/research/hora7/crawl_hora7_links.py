import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(wait_until="domcontentloaded", delay_before_return_html=2.0)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url="https://hora-7-of-9-base.vercel.app/", config=run_cfg)
        print("status:", result.success)
        # list links
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(result.html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            links.append({"text": a.get_text(strip=True)[:120], "href": a["href"]})
        # dedupe
        seen = set()
        uniq = []
        for l in links:
            if l["href"] not in seen:
                seen.add(l["href"])
                uniq.append(l)
        # print some
        print("\n--- LINKS ---")
        for l in uniq[:100]:
            print(l["text"], "=>", l["href"])
        # headings
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])]
        print("\n--- HEADINGS ---")
        for h in headings:
            print("-", h)

asyncio.run(main())
