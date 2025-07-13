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

# ✅ 預設情緒分類
DEFAULT_EMOTIONS = card_df["emotion"].unique().tolist()

def process_dream(user_input: str, user_id: str = None):
    try:
        # ✅ 呼叫 Gemini API 分析夢境 + 情緒
        gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        gemini_response = gemini_model.generate_content([
            {
                "role": "user",
                "parts": [
                    f"請根據以下夢境內容，提供心理學觀點的解析，語氣溫柔療癒，限制在 5 行內。\n"
                    f"夢境：{user_input}\n"
                    f"請另外回覆這個夢境可能對應的情緒，僅限以下情緒中的一種：{', '.join(DEFAULT_EMOTIONS)}。\n"
                    f"格式如下：\n說明：xxx\n情緒：xxx"
                ]
            }
        ])

        gemini_text = gemini_response.text.strip()
        gemini_text = gemini_text.encode("utf-8", "ignore").decode("utf-8")

        # ✅ 拆解 Gemini 回傳格式
        explain_part = ""
        emotion_part = ""
        for line in gemini_text.splitlines():
            if line.startswith("說明："):
                explain_part = line.replace("說明：", "").strip()
            elif line.startswith("情緒："):
                emotion_part = line.replace("情緒：", "").strip()

        # ✅ 防呆處理
        if not explain_part:
            explain_part = "（無法解析說明）"
        if emotion_part not in DEFAULT_EMOTIONS:
            emotion_part = random.choice(DEFAULT_EMOTIONS)

    except Exception as e:
        explain_part = "⚠️ 無法使用 Gemini 補充夢境說明"
        emotion_part = random.choice(DEFAULT_EMOTIONS)
        print(f"[Gemini Error] {str(e)}")

    # ✅ 根據情緒抽一張命定卡牌
    emotion_cards = card_df[card_df["emotion"] == emotion_part]
    if not emotion_cards.empty:
        card = emotion_cards.sample(1).iloc[0]
        card_title = card["title"]
        card_message = card["message"]
        card_image = card["image"]
    else:
        card_title = "無卡牌"
        card_message = ""
        card_image = ""

    # ✅ DEBUG 輸出
    debug_output = {
        "text": explain_part,
        "emotion": emotion_part,
        "title": card_title,
        "message": card_message,
        "image": card_image
    }
    print("[DEBUG] 回傳內容：", debug_output)

    return debug_output
