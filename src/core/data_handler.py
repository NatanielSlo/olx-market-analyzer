import json
import os


from src.utils.postgres_uploader import PostgresUploader
from src.utils.DataProcessors.base_processor import BaseProcessor
from src.utils.DataProcessors.iphone_processor import IphoneProcessor

from src.config import OUTPUT_FILE

async def analyze_data():
    input_file = OUTPUT_FILE

    baseprocessor = BaseProcessor()
    iphoneprocessor = IphoneProcessor()
    postgres_uploader= PostgresUploader()
    
    if not os.path.exists(input_file):
        print(f"Błąd: Plik {input_file} nie istnieje.")
        return

    print("Rozpoczynam analizę i oczyszczanie danych...")
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        
        proccessed_data = []

        for line in infile:
            try:
                # 1. Wczytaj linię (pojedynczy JSON)
                item = json.loads(line)
                
                # 2. Oczyszczanie ceny (zamiana na int/float)
                if item.get('price'):
                    item['price_numeric'] = int(''.join(filter(str.isdigit, item['price'])))
                
                storage_raw = item.get('wbudowana_pamięć')
                item['storage_gb'] = baseprocessor.clean_storage(storage_raw)
                
                description = item.get('description', '')
                item['battery_health'] = iphoneprocessor.extract_battery_health(description)
                
                proccessed_data.append(item)
            except Exception as e:
                print(f"Pominęto linię z powodu błędu: {e}")

    print(f"Analiza zakończona. Rozpoczynam proces publikowania danych do bazy")

    # Filter duplicates
    unique_items = {}
    for item in proccessed_data:
        url = item.get('url')
        if url:
            unique_items[url] = item

    final_data = list(unique_items.values())


    postgres_uploader.connect_postgres()
    postgres_uploader.upload_to_postgres(final_data)
    postgres_uploader.close_connection()

