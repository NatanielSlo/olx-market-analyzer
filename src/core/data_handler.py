import json
import os

from src.utils.DataProcessors.base_processor import BaseProcessor
from src.utils.DataProcessors.iphone_processor import IphoneProcessor

from src.config import INPUT_FILE, OUTPUT_FILE

async def analyze_data():
    input_file = INPUT_FILE
    output_file = OUTPUT_FILE

    baseprocessor = BaseProcessor()
    iphoneprocessor = IphoneProcessor()
    
    if not os.path.exists(input_file):
        print(f"Błąd: Plik {input_file} nie istnieje.")
        return

    print("Rozpoczynam analizę i oczyszczanie danych...")
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
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
                item['battery_health'] = iphoneprocessor.extract_battery(description)
                
                outfile.write(json.dumps(item, ensure_ascii=False) + '\n')
                
            except Exception as e:
                print(f"Pominęto linię z powodu błędu: {e}")

    print(f"Analiza zakończona. Oczyszczone dane zapisano w: {output_file}")