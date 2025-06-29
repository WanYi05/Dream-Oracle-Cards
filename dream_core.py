import random
import os
from datetime import datetime
from dotenv import load_dotenv  # ✅ 載入 .env
from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from oracle_engine import draw_card
from utils import save_result

from linebot.v3 import Configuration
from linebot.v3.messaging import MessagingApi, ApiClient, TextMessage

# ✅ 載入 .env 檔
load_dotenv()

# ✅ 備用卡牌圖片清單
ALL_CARD_IMAGES = [
    "A1.jpg", "A2.jpg", "A3.jpg", "B1.jpg", "B2.jpg", "B3.jpg", "C1.jpg", "C2.jpg", "c3.jpg", "D1.jpg", "D2.jpg", "D3.jpg",
    "E1.jpg", "E2.jpg", "E3.jpg", "F1.jpg", "F2.jpg", "F3.jpg", "G1.jpg", "G2.jpg", "G3.jpg", "H1.jpg", "H2.jpg", "H3.jpg",
    "I1.jpg", "I2.jpg", "I3.jpg", "J1.jpg", "J2.jpg", "J3.jpg", "K1.jpg", "K2.jpg", "K3.jpg", "L1.jpg", "L2.jpg", "L3.jpg",
    "M1.jpg", "M2.jpg", "M3.jpg", "N1.jpg", "N2.jpg", "N3.jpg", "O1.jpg", "O2.jpg", "O3.jpg", "P1.jpg", "P2.jpg", "P3.jpg"
]

def log_missing_keyword(keyword, user_id=None):
    log_dir = "output"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "missing_keywords.log")
    log_line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {user_id or 'anonymous'} | {keyword}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line)
    print(f"[MISSING LOG] {log_line.strip()}")

def notify_developer(keyword, user_id=None):
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    developer_user_id = os.getenv("DEVELOPER_USER_ID")

    if not access_token or not developer_user_id:
        print("[WARNING] 環境變數 LINE_CHANNEL_ACCESS_TOKEN 或 DEVELOPER_USER_ID 未設定，無法推播")
        return

    message = f"🛑 使用者 {user_id or 'unknown'} 查詢「{keyword}」，但查無解夢資料"
    try:
        configuration = Configuration(access_token=access_token)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.push_message(
                to=developer_user_id,
                messages=[TextMessage(text=message)]
            )
        print(f"[PUSH] 已推送通知給開發者：{message}")
    except Exception as e:
        print(f"[ERROR] 發送開發者推播時出錯：{e}")

def process_dream(keyword, user_id=None):
    dream_text = get_dream_interpretation(keyword)

    print(f"📥 使用者輸入關鍵字：{keyword}")
    print(f"🧠 解夢結果：{dream_text}")

    if dream_text.startswith("⚠️"):
        # ⛔ 無解夢資料：寫入 log 並推播開發者
        log_missing_keyword(keyword, user_id)
        notify_developer(keyword, user_id)

        emotion = "未知"
        card = {
            "title": "無法對應情緒",
            "message": "👉 目前僅支援特定情緒，將為你抽一張隨機命定卡。",
            "image": random.choice(ALL_CARD_IMAGES)
        }
    else:
        # ✅ 正常解析情緒並抽卡
        emotion = map_emotion(dream_text)
        card = draw_card(emotion)

    # ✅ 儲存記錄
    save_result(keyword, dream_text, emotion, card)

    # ✅ 組合回應文字
    text = f"""🔍 解夢關鍵字：{keyword}
🧠 解夢結果：
{dream_text}

🎭 情緒判定：{emotion}
🃏 命定卡牌：「{card['title']}」
👉 {card['message']}"""

    return {
        "text": text,
        "image": card["image"]
    }

# ✅ 本機測試區塊
if __name__ == "__main__":
    test_keyword = "火鍋寶寶外星人"  # 輸入不存在的關鍵字來觸發 missing log
    result = process_dream(test_keyword, user_id="LocalTest")
    print("\n====== 測試結果 ======\n")
    print(result["text"])
    print(f"\n🖼️ 圖片檔名：{result['image']}")
