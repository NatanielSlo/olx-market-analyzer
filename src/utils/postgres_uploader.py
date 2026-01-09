from src.config import DB_CONFIG
import psycopg2


from psycopg2.extras import execute_values
from datetime import datetime

class PostgresUploader:
    def __init__(self):
        pass

    def connect_postgres(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        print("Connection to postgres established")


    def upload_to_postgres(self,processed_items):
        self.create_tables()
        """
        Przyjmuje aktywne połączenie (conn) oraz listę słowników (processed_items).
        Publikuje dane w bazie używając techniki batch insert (szybkie wstawianie masowe).
        """
        
        # SQL UPSERT: Wstawia nowe, a przy konflikcie URL aktualizuje cenę i datę.
        upsert_query = """
            INSERT INTO iphone_offers (url, title, price, battery_health, storage_gb, last_seen)
            VALUES %s
            ON CONFLICT (url) 
            DO UPDATE SET 
                price = EXCLUDED.price,
                last_seen = EXCLUDED.last_seen,
                battery_health = COALESCE(EXCLUDED.battery_health, iphone_offers.battery_health);
        """

        # Przygotowujemy dane: zamieniamy listę słowników na listę krotek (wartości w nawiasach)
        # To jest format, który rozumie funkcja execute_values
        data_to_insert = [
            (
                item.get('url'),
                item.get('title'),
                item.get('price_numeric'),
                item.get('battery_health'),
                item.get('storage_gb'),
                datetime.now() # To wpada do kolumny last_seen
            ) for item in processed_items
        ]

        try:
            cur = self.conn.cursor()
            # execute_values jest znacznie szybsze niż pętla for i zwykłe execute
            execute_values(cur, upsert_query, data_to_insert)
            self.conn.commit()
            cur.close()
            print(f"Baza zaktualizowana: dodano/odświeżono {len(data_to_insert)} ofert.")
        except Exception as e:
            self.conn.rollback() # W razie błędu wycofujemy zmiany
            print(f"Błąd podczas publikacji w bazie: {e}")


    def close_connection(self):
        self.cur.close()
        self.conn.close()
        print("Connection to postgres closed")


    def create_tables(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS iphone_offers (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            price INTEGER,
            battery_health INTEGER,
            storage_gb INTEGER,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            cur = self.conn.cursor()
            cur.execute(create_table_query)
            self.conn.commit()
            cur.close()
            print("Tabela 'iphone_offers' jest gotowa.")
        except Exception as e:
            print(f"Błąd podczas tworzenia tabeli: {e}")