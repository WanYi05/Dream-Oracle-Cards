import random
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

# ✅ 載入 .env 檔案取得 GEMINI API KEY
load_dotenv(dotenv_path=Path(".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ 載入卡牌資料
CARDS_CSV_PATH = "emotion_cards_full.csv"
card_df = pd.read_csv(CARDS_CSV_PATH)

# ✅ 預設情緒分類（可依照實際需求調整）
DEFAULT_EMOTIONS = card_df["emotion"].unique().tolist()


def process_dream(user_input: str, user_id: str = None):
    reply_text = f"🔍 解夢關鍵字：{user_input}"

    # ✅ 使用 Gemini 解釋夢境 + 分析情緒
    try:
        gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        gemini_response = gemini_model.generate_content([
            {
                "role": "user",
                "parts": [
                    f"請根據以下夢境內容，提供心理學觀點的解析，語氣溫柔療癒，限制在 5 行內。\n夢境：{user_input}\n請另外回覆這個夢境可能對應的情緒，僅限以下情緒中的一種：{', '.join(DEFAULT_EMOTIONS)}。\n格式如下：\n說明：xxx\n情緒：xxx"
                ]
            }
        ])

        gemini_text = gemini_response.text.strip()
        gemini_text = gemini_text.encode("utf-8", "ignore").decode("utf-8")

        # ✅ 拆解 Gemini 回傳內容
        explain_part = ""
        emotion_part = ""
        for line in gemini_text.splitlines():
            if line.startswith("說明："):
                explain_part = line.replace("說明：", "").strip()
            elif line.startswith("情緒："):
                emotion_part = line.replace("情緒：", "").strip()

        reply_text += f"\n🧠 解夢結果：{explain_part}"
        reply_text += f"\n🎭 情緒判定：{emotion_part}"

    except Exception as e:
        reply_text += "\n⚠️ 無法使用 Gemini 補充夢境說明"
        emotion_part = random.choice(DEFAULT_EMOTIONS)
        print(f"[Gemini Error] {str(e)}")

    # ✅ 從情緒分類中隨機抽取一張卡
    emotion_cards = card_df[card_df["emotion"] == emotion_part]
    if not emotion_cards.empty:
        card = emotion_cards.sample(1).iloc[0]
        card_title = card["title"]
        card_message = card["message"]
        card_image = card["image"]

        reply_text += f"\n🃏 命定卡牌：「{card_title}」"
        reply_text += f"\n👉 {card_message}"
    else:
        card_image = None
        reply_text += f"\n⚠️ 查無對應「{emotion_part}」情緒的卡牌"

    return {
        "text": reply_text,
        "image": card_image
    }
