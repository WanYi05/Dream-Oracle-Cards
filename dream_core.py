# dream_core.py

import random
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from utils import save_result

# ✅ 載入 .env 環境變數
load_dotenv()

# ✅ 備用卡牌圖片清單（請放在 /Cards 資料夾中）
ALL_CARD_IMAGES = [
    "A1.jpg", "A2.jpg", "A3.jpg", "B1.jpg", "B2.jpg", "B3.jpg", "C1.jpg", "C2.jpg", "C3.jpg",
    "D1.jpg", "D2.jpg", "D3.jpg", "E1.jpg", "E2.jpg", "E3.jpg", "F1.jpg", "F2.jpg", "F3.jpg",
    "G1.jpg", "G2.jpg", "G3.jpg", "H1.jpg", "H2.jpg", "H3.jpg", "I1.jpg", "I2.jpg", "I3.jpg",
    "J1.jpg", "J2.jpg", "J3.jpg", "K1.jpg", "K2.jpg", "K3.jpg", "L1.jpg", "L2.jpg", "L3.jpg",
    "M1.jpg", "M2.jpg", "M3.jpg", "N1.jpg", "N2.jpg", "N3.jpg", "O1.jpg", "O2.jpg", "O3.jpg",
    "P1.jpg", "P2.jpg", "P3.jpg"
]

# ✅ 載入完整卡牌資料（含情緒、標題、訊息、圖片）
CARDS_DF = pd.read_csv(Path(__file__).parent / "emotion_cards_full.csv")

def get_emotion_card(emotion: str):
    """
    從 emotion_cards_full.csv 中依情緒抽卡，若無對應則隨機抽一張。
    """
    emotion_clean = emotion.strip()
    if emotion_clean in CARDS_DF["emotion"].unique():
        matched = CARDS_DF[CARDS_DF["emotion"] == emotion_clean]
        result = matched.sample().to_dict("records")[0]
        return {
            "title": result["title"],
            "message": result["message"],
            "image": result.get("image", random.choice(ALL_CARD_IMAGES))
        }
    else:
        result = CARDS_DF.sample().to_dict("records")[0]
        return {
            "title": "無法對應情緒",
            "message": "✨ 目前僅支援特定情緒，這是隨機卡牌：\n\n☞ {}\n✨ {}".format(result["title"], result["message"]),
            "image": result.get("image", random.choice(ALL_CARD_IMAGES))
        }

def log_missing_keyword(keyword, user_id=None):
    log_path = Path(__file__).parent / "missing_keywords.log"
    log_line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {user_id or 'anonymous'} | {keyword}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(f"[MISSING LOG] {log_line.strip()}")
    except Exception as e:
        print(f"[ERROR] 寫入 log 檔失敗：{e}")

def notify_developer(keyword, user_id=None):
    try:
        access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        developer_user_id = os.getenv("DEVELOPER_USER_ID")

        if not access_token or not developer_user_id:
            print("[WARNING] 環境變數未設定，跳過開發者通知")
            return

        # from linebot.v3 import Configuration
        from linebot.v3.messaging.rest import Configuration
        from linebot.v3.messaging import MessagingApi, ApiClient, TextMessage

        configuration = Configuration(access_token=access_token)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            message = f"🛑 使用者 {user_id or 'unknown'} 查詢「{keyword}」，但查無解夢資料"
            line_bot_api.push_message(
                to=developer_user_id,
                messages=[TextMessage(text=message)]
            )
        print(f"[PUSH] 已推送通知給開發者")

    except Exception as e:
        print(f"[SKIPPED] 推播功能錯誤已略過：{e}")

def process_dream(keyword, user_id=None):
    dream_text = get_dream_interpretation(keyword)

    if dream_text.startswith("⚠️"):
        log_missing_keyword(keyword, user_id)
        notify_developer(keyword, user_id)
        emotion = "未知"
        card = get_emotion_card(emotion)
    else:
        emotion = map_emotion(dream_text)
        card = get_emotion_card(emotion)

        if not all(k in card for k in ["title", "message", "image"]):
            card = {
                "title": "資料錯誤",
                "message": "⚠️ 系統未能正確取得卡片內容。",
                "image": random.choice(ALL_CARD_IMAGES)
            }

    save_result(keyword, dream_text, emotion, card)

    text = f"""\U0001f50d 解夢關鍵字：{keyword}
🧠 解夢結果：
{dream_text}

🎭 情緒判定：{emotion}
🃏 命定卡片：「{card['title']}」
👉 {card['message']}"""

    return {
        "text": text,
        "image": card["image"],
        "emotion": emotion,               # ✅ 加上情緒
        "title": card["title"],           # ✅ 加上卡牌標題
        "message": card["message"]        # ✅ 加上卡牌訊息
    }


# # ✅ 本機測試入口（可本地執行檢查）
# if __name__ == "__main__":
#     test_keyword = "火鍋寶寶外星人"
#     result = process_dream(test_keyword, user_id="LocalTest")
#     print("\n====== 測試結果 ======\n")
#     print(result["text"])
#     print(f"\n🖼️ 圖片檔名：{result['image']}")
