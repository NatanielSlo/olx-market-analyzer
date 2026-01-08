import json
import os
import random
import asyncio

from src.utils.url_builder import UrlBuilder
from src.core.pages.search_page import SearchPage

from playwright.async_api import async_playwright

from src.config import INPUT_FILE, USER_AGENT, HEADLESS_MODE, KEY_WORD, QUERY, PHONE_MODEL, MIN_PRICE, PAGE_LIMIT,SCRAPE_DELAY_MAX,SCRAPE_DELAY_MIN,ERROR_TIMEOUT

class GeneralScraper:
    def __init__(self):
        # Parametry wyszukiwania
        self.key_word = KEY_WORD
        self.query = QUERY
        self.phone_model = PHONE_MODEL
        self.min_price = MIN_PRICE
        self.page_limit = PAGE_LIMIT
        
        # Narzędzia (zainicjalizowane jako None, stworzymy je w start())
        self.url_builder = UrlBuilder()
        self.browser = None
        self.context = None
        self.page = None
        self.search_page = None

        self.all_results = []
        
        # Dane
        self.data_file = INPUT_FILE

    async def start(self):
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=HEADLESS_MODE)
        
        # Konfiguracja stealth i kontekstu
        self.context = await self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Blokowanie zbędnych zasobów (opcjonalnie, dla szybkości)
        await self.context.route("**/*", lambda route: 
            route.abort() if route.request.resource_type in ["image", "media", "font"] 
            else route.continue_()
        )
        
        self.page = await self.context.new_page()
        self.search_page = SearchPage(self.page)
        print("Przeglądarka gotowa do pracy.")

    async def run_search(self):

        if not self.page:
            await self.start()

        
        for page_num in range(1, self.page_limit + 1):
            url = self.url_builder.build_search_url(
                self.query, page_num, phone_model=self.phone_model
            )
            
            await self.page.goto(url, wait_until="domcontentloaded")
            
            
            if await self._check_for_blocks(url):
                continue
            if await self._is_end_of_results(page_num):
                break
            
            new_products = await self.search_page.get_all_products(
                5, self.key_word, self.min_price
            )
            self.all_results.extend(new_products)
            
            
            self.save_to_json(new_products,page_num)
            
            await self.page.wait_for_timeout(random.randint(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX))
        
        await self.stop()

    async def stop(self):
        if self.browser:
            
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            
            
            await self.browser.close()
            print("Przeglądarka zamknięta.")
            
            await asyncio.sleep(0.5)

    async def _check_for_blocks(self,url):
        is_403 = await self.page.locator("h1:has-text('403 ERROR')").is_visible()

        while is_403:
            await self.page.wait_for_timeout(ERROR_TIMEOUT)
            await self.page.goto(url, wait_until="domcontentloaded")
            is_403 = await self.page.locator("h1:has-text('403 ERROR')").is_visible()
            print("Cought 403 error")           

    async def _is_end_of_results(self,page_num):
        if f"page={page_num}" not in self.page.url and page_num > 1:
            print(f"Przekierowano na inną stronę (prawdopodobnie koniec wyników). Kończę.")
            self.save_to_json()
            return True
        if page_num==self.page_limit:
            self.save_to_json()
            print("stopped scraping because of testing limits")
            return True
        return False

    def save_to_json(self,new_products=None,page_num = None):
        
        file_path = self.data_file

        data_to_save = new_products if new_products is not None else self.all_results

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []
            except (json.JSONDecodeError, Exception):
                existing_data = []
        else:
            existing_data = []

        existing_urls = {item['url'] for item in existing_data}
        unique_new_products = [p for p in data_to_save if p['url'] not in existing_urls]
        
        combined_data = existing_data + unique_new_products

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=4, ensure_ascii=False)
        
        print(f"Analiza strony: {page_num} Zapisano. Nowych: {len(unique_new_products)}, Łącznie w pliku: {len(combined_data)}")

