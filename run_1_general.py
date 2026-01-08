from src.core.general_scraper import GeneralScraper

import asyncio

async def run():
    general_scraper = GeneralScraper()
    await general_scraper.run_search()

if __name__ == "__main__":
    asyncio.run(run())