import json
import dateparser
import random
import asyncio
import time
import os
from src.utils.url_builder import UrlBuilder
from datetime import datetime

from playwright.async_api import async_playwright
from playwright_stealth import Stealth


from src.config import INPUT_FILE, OUTPUT_FILE, USER_AGENT,HEADLESS_MODE,MAX_CONCURRENT_PAGES,SCRAPE_DELAY_MAX,SCRAPE_DELAY_MIN,ERROR_TIMEOUT

class DetailsScraper:
    def __init__(self):

        self.input_path = INPUT_FILE
        self.output_path = OUTPUT_FILE

        self.browser = None
        self.context = None
        self.url_builder = UrlBuilder()

        self.lock = asyncio.Lock()

        self.total_to_do = 0
        self.completed_count = 0
        self.finished_urls = set()
        self.data = []



    async def start(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=HEADLESS_MODE) 
        
        self.context = await self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1280, 'height': 800}
        )
        
        # Blokada mediów dla oszczędności transferu
        await self.context.route("**/*", lambda route: 
            route.abort() if route.request.resource_type in ["image", "media", "font"] 
            else route.continue_()
        )
        
        self.reload_data()

    def _load_finished_urls(self, filename):
        urls = set()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        urls.add(json.loads(line)["url"])
                    except: continue
        return urls
    

    def _load_data(self,filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Failed loading data, from {filename}")
            return []
        
    async def _save_incremental(self, item):
        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


    def reload_data(self):
        print(f"Reading {self.input_path} before scraping details")
        self.data = self._load_data(self.input_path)
        self.finished_urls = self._load_finished_urls(self.output_path)

    async def get_product_details_parallel(self):
        await self.start()
        start_time = time.perf_counter()
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)

        tasks_to_do = [item for item in self.data if item['url'] not in self.finished_urls]

        print(f"Do pobrania: {len(tasks_to_do)} produktów (Równolegle: {MAX_CONCURRENT_PAGES})")
        self.total_to_do = len(tasks_to_do)
        self.completed_count = 0

        tasks = [self.process_single_item(item, semaphore) for item in tasks_to_do]
        await asyncio.gather(*tasks)

        end_time = time.perf_counter() 
        total_duration = end_time - start_time

        print("-" * 30)
        print(f"Zakończono pobieranie danych!")
        print(total_duration)
        print("-" * 30)


    async def _check_for_blocks(self,url):
        is_403 = await self.page.locator("h1:has-text('403 ERROR')").is_visible()

        while is_403:
            await self.page.wait_for_timeout(ERROR_TIMEOUT)
            await self.page.goto(url, wait_until="domcontentloaded")
            is_403 = await self.page.locator("h1:has-text('403 ERROR')").is_visible()
            print("Cought 403 error")    

    async def process_single_item(self, item, semaphore):
        async with semaphore:

            await asyncio.sleep(random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX))
            
            page = await self.context.new_page()
            
            url = self.url_builder.build_product_url(item.get('url'))
    

            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)

                await self._check_for_blocks()
                
                # Opis
                desc_loc = page.locator(".css-19duwlz")
                if await desc_loc.count() > 0:
                    item["description"] = (await desc_loc.inner_text(timeout=5000)).replace("\n", " ")

                # Data
                date_loc = page.locator(".css-7b83xv")
                if await date_loc.count() > 0:
                    date_text = await date_loc.inner_text(timeout=5000)
                    date_obj = dateparser.parse(date_text)
                    if date_obj:
                        item["date"] = date_obj.strftime("%d.%m.%Y")

                # Parametry
                params_container = page.locator('[data-testid="ad-parameters-container"]')
                if await params_container.count() > 0:
                    params = await params_container.locator('p.css-13x8d99').all()
                    for p in params:
                        text = await p.inner_text()
                        if ":" in text:
                            k, v = text.split(":", 1)
                            item[k.strip().lower().replace(" ", "_")] = v.strip()
                        else:
                            item["typ_oferty"] = text.strip()

                if item.get("description"):
                    item["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await self._save_incremental(item)
                    self.finished_urls.add(item['url'])
                    self.completed_count += 1
                    procent = (self.completed_count / self.total_to_do) * 100
                    print(f"[{self.completed_count}/{self.total_to_do}] {procent:.1f}% | ✔️ Gotowe: {url[-15:]}")
                
            except Exception as e:
                print(f"  Błąd {url}: {e}")
            finally:
                await page.close()



        

