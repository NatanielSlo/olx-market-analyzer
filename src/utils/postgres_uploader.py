from src.config import DB_CONFIG
import psycopg2


class PostgresUploader:
    def __init__(self):
        pass

    def connect_postgres(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()


    def create_table(self):
        self.cur.execute("""
""")


    def close_connection(self):
        self.cur.close()
        self.conn.close()

