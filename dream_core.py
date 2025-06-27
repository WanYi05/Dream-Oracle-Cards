# dream_core.py
import random
from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from oracle_engine import draw_card
from utils import save_result

# 備用卡牌圖片清單（請依實際圖片命名調整）
ALL_CARD_IMAGES = [
    "A1.jpg", "A2.jpg", "B1.jpg", "B2.jpg", "C1.jpg", "D1.jpg",
    "E1.jpg", "F1.jpg", "G1.jpg", "H1.jpg"
]

def process_dream(keyword):
    dream_text = get_dream_interpretation(keyword)

    if dream_text.startswith("⚠️"):
        emotion = "未知"
        card = {
            "title": "無法對應情緒",
            "message": "👉 目前僅支援特定情緒，將為你抽一張隨機命定卡。",
            "image": random.choice(ALL_CARD_IMAGES)
        }
    else:
        emotion = map_emotion(dream_text)
        card = draw_card(emotion)

    save_result(keyword, dream_text, emotion, card)

    # 文字訊息內容
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
