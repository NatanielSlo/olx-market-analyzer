import os

# --- ŚCIEŻKI DO PLIKÓW ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "data.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "extended_data.jsonl")

# --- PARAMETRY WYSZUKIWANIA (OLX) ---
QUERY = "iphone"
KEY_WORD = "15"
PHONE_MODEL = "iphone-15-pro"
MIN_PRICE = 1800  
PAGE_LIMIT = 5

# --- PARAMETRY SCRAPINGU ---
MAX_CONCURRENT_PAGES = 5
HEADLESS_MODE = False  
SCRAPE_DELAY_MIN = 3
SCRAPE_DELAY_MAX = 7
ERROR_TIMEOUT = 50000



# --- KONFIGURACJA PRZEGLĄDARKI ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."