import json
import os
import asyncio

from src.config import INPUT_FILE

class SearchPage:
    def __init__(self, page):
        self.page = page
        self.listing_grid = page.get_by_test_id("listing-grid")
        self.product_card = page.get_by_test_id("l-card")

        self.data_file = INPUT_FILE




    def _get_existing_urls(self):
        if not os.path.exists(self.data_file):
            return set()
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                return {item['url'] for item in existing_data if 'url' in item}
        except (json.JSONDecodeError, Exception):
            return set()


    async def _parse_card(self,card,key_word,price_threshold,existing_urls):
        try:
            title_node = card.locator(".css-hzlye5")
            link_node = card.locator("a.css-1tqlkj0").first

            title, link = await asyncio.gather(
                title_node.inner_text(timeout=1000),
                link_node.get_attribute("href", timeout=1000)
            )
            if link in existing_urls: return None
            if key_word not in title.lower() or link in existing_urls: return None

            price_raw = await card.get_by_test_id("ad-price").inner_text(timeout=500)
            price_clean = price_raw.split("zł")[0].split(",")[0].replace(" ", "").replace("\xa0", "").strip()
            
            try:
                price_int = int(price_clean)
            except ValueError:
                return None

            if price_int < price_threshold:
                return None

            return {
                "title": title,
                "price": price_clean,
                "url": link
            }
        except:
            return None


    async def get_all_products(self,products_num,key_word,price_threshold):
        
        existing_urls = self._get_existing_urls()

        await self.listing_grid.wait_for()
        cards = await self.product_card.all()

        tasks = [self._parse_card(card, key_word, price_threshold, existing_urls) for card in cards]
        
        scraped_data = []

        results = await asyncio.gather(*tasks)

        scraped_data = [r for r in results if r is not None]

        return scraped_data
    

