# database.py
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dream_logs (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            keyword TEXT,
            emotion TEXT,
            timestamp TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def write_to_postgres(user_id, keyword, emotion):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    #台灣時間
    taiwan_time = datetime.now(timezone(timedelta(hours=8)))

    cursor.execute("""
        INSERT INTO dream_logs (user_id, keyword, emotion, timestamp) 
        VALUES (%s, %s, %s, %s)
    """, (user_id, keyword, emotion, taiwan_time))

    conn.commit()
    conn.close()

def get_all_logs():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, keyword, emotion, timestamp
        FROM dream_logs 
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
