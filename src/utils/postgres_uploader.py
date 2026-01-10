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


    def filter_new_and_update_seen(self, scraped_products):

        if not scraped_products:
            return []

        # Wyciągamy same URL-e do sprawdzenia, co już mamy
        urls = [p['url'] for p in scraped_products]
        
        try:
            cur = self.conn.cursor()
            
            cur.execute("SELECT url FROM iphone_offers WHERE url = ANY(%s)", (urls,))
            existing_urls = {row[0] for row in cur.fetchall()}
            
            new_products = [p for p in scraped_products if p['url'] not in existing_urls]
            old_products_urls = [p['url'] for p in scraped_products if p['url'] in existing_urls]
            
            if old_products_urls:
                # Przygotowujemy dane do update (lista krotek: nowa_data, url)
                now = datetime.now()
                update_data = [(now, url) for url in old_products_urls]
                
                # Używamy execute_values do masowego update'u
                update_query = """
                    UPDATE iphone_offers 
                    SET last_seen = data.ls
                    FROM (VALUES %s) AS data(ls, u)
                    WHERE url = data.u;
                """
                from psycopg2.extras import execute_values
                execute_values(cur, update_query, update_data)
                
                print(f"Zaktualizowano 'last_seen' dla {len(old_products_urls)} znanych ofert.")

            self.conn.commit()
            cur.close()
            
            return new_products 
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Błąd bazy danych przy filtrowaniu/aktualizacji: {e}")
            return []