# database.py
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def write_to_postgres(keyword, emotion):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dream_logs (
            id SERIAL PRIMARY KEY,
            keyword TEXT,
            emotion TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("INSERT INTO dream_logs (keyword, emotion) VALUES (%s, %s)", (keyword, emotion))
    conn.commit()
    conn.close()
