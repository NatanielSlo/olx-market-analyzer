from src.core.details_scraper import DetailsScraper
import asyncio


async def run():
    details_scraper = DetailsScraper()
    await details_scraper.get_product_details_parallel()


if __name__ == "__main__":
    asyncio.run(run())