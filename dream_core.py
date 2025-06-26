# dream_core.py
from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from oracle_engine import draw_card
from utils import save_result

def process_dream(keyword):
    dream_text = get_dream_interpretation(keyword)

    if dream_text.startswith("⚠️"):
        emotion = "未知"
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

    # 回傳文字 + 圖片
    return {
        "text": text,
        "image": card["image"]  # 例如 "A1.jpg"
    }
