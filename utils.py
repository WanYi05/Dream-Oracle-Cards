import sqlite3
import os
from datetime import datetime

# 資料庫路徑
DB_PATH = "output/dream_log.db"

def init_db():
    """
    初始化 SQLite 資料庫與資料表
    """
    # 確保 output 資料夾存在
    output_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 建立資料表
    c.execute('''
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            keyword TEXT,
            emotion TEXT,
            title TEXT,
            message TEXT,
            dream_text TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_result(keyword, dream_text, emotion, card):
    """
    儲存一筆抽卡結果到 SQLite 資料庫
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        INSERT INTO draws (timestamp, keyword, emotion, title, message, dream_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        keyword,
        emotion,
        card["title"],
        card["message"],
        dream_text
    ))

    conn.commit()
    conn.close()
