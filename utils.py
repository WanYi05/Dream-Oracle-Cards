import csv
import os
from datetime import datetime

# 設定新的 CSV 檔案名稱
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cardoutput.csv")

def init_db():
    """
    初始化 CSV 資料夾與 cardoutput.csv 檔案（若不存在則建立）
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.isfile(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "keyword", "emotion", "title", "message", "dream_text"
            ])

def save_result(keyword, dream_text, emotion, card):
    """
    將抽卡結果寫入 cardoutput.csv 檔案
    """
    with open(OUTPUT_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            keyword,
            emotion,
            card["title"],
            card["message"],
            dream_text
        ])
