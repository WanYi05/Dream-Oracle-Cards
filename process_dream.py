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
try:
    card_df = pd.read_csv(CARDS_CSV_PATH)
except Exception as e:
    print(f"❌ 無法讀取卡牌資料: {str(e)}")
    card_df = pd.DataFrame(columns=["emotion", "title", "message", "image"])

# ✅ 預設情緒分類
DEFAULT_EMOTIONS = card_df["emotion"].unique().tolist() if not card_df.empty else []

def process_dream(user_input: str, user_id: str = None):
    explain_part = "⚠️ 尚未支援此夢境，請稍後再試或由開發者補充資料"
    emotion_part = "未知"
    card_title = "無法對應情緒"
    card_message = "👉 目前僅支援特定情緒，將為你抽一張隨機命定卡。"
    card_image = ""

    try:
        # ✅ Gemini 回應
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

        for line in gemini_text.splitlines():
            if line.startswith("說明："):
                explain_part = line.replace("說明：", "").strip()
            elif line.startswith("情緒："):
                emotion_part = line.replace("情緒：", "").strip()

        # ✅ 情緒不在列表內就隨機挑一個
        if emotion_part not in DEFAULT_EMOTIONS:
            emotion_part = random.choice(DEFAULT_EMOTIONS)

    except Exception as e:
        print(f"[Gemini Error] {str(e)}")
        explain_part = "⚠️ 無法使用 Gemini 補充夢境說明"
        if DEFAULT_EMOTIONS:
            emotion_part = random.choice(DEFAULT_EMOTIONS)

    # ✅ 從卡牌資料中根據情緒抽一張
    emotion_cards = card_df[card_df["emotion"] == emotion_part]
    if not emotion_cards.empty:
        card = emotion_cards.sample(1).iloc[0]
        card_title = card.get("title", card_title)
        card_message = card.get("message", card_message)
        card_image = card.get("image", card_image)

    # ✅ 回傳統一格式，確保不會出現 KeyError
    result = {
        "text": explain_part,
        "emotion": emotion_part,
        "title": card_title,
        "message": card_message,
        "image": card_image
    }

    return result
