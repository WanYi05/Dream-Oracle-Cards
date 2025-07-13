from flask import Flask, request, abort, send_from_directory
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import google.generativeai as genai

# ✅ 載入 .env 檔案
load_dotenv(dotenv_path=Path(".env"))

# ✅ 設定 Gemini API KEY
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ 環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET]):
    raise EnvironmentError("❌ 請確認 .env 是否正確設定 LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = Flask(__name__)

@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

@app.route("/", methods=["GET"])
def index():
    return "🌙 Dream Oracle LINE BOT 正在運行中！"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("⚠️ Invalid signature.")
        abort(400)
    except Exception as e:
        app.logger.error(f"🔥 其他錯誤：{str(e).encode('utf-8', 'ignore').decode('utf-8')}")
        abort(500)

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print("👤 使用者 ID：", user_id)

    try:
        if user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="👋 感謝使用 Dream Oracle，再會～")]

        else:
            # ✅ 直接使用 Gemini API 解釋夢境
            try:
                gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                gemini_response = gemini_model.generate_content(
                    f"使用溫柔、療癒的語氣，釋解夢境「{user_input}」的賢察和心理意義，限制在 5 行以內。"
                )
                reply_text = gemini_response.text.strip()
                reply_text = reply_text.encode("utf-8", "ignore").decode("utf-8")
            except Exception as ge:
                reply_text = "⚠️ 無法解析夢境，請稍候重試"
                print(f"[Gemini Error] {str(ge).encode('utf-8', 'ignore').decode('utf-8')}")

            # ✅ 分段回覆阿拉長訊息
            messages = []
            max_length = 4900
            for i in range(0, len(reply_text), max_length):
                messages.append(TextMessage(text=reply_text[i:i+max_length]))

        # ✅ 回覆 LINE 使用者
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )

    except Exception as e:
        print(f"[ERROR] 回傳訊息失敗：{str(e).encode('utf-8', 'ignore').decode('utf-8')}")

if __name__ == "__main__":
    app.run(port=5001)