# bot_app.py

from flask import Flask, request, abort, send_from_directory
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import os
import json

from dream_core import process_dream

# ✅ 載入 .env 檔案
load_dotenv(dotenv_path=Path(".env"))

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DEVELOPER_USER_ID = os.getenv("DEVELOPER_USER_ID")

# ✅ 檢查必要環境變數
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET]):
    raise EnvironmentError("❌ 請確認 .env 是否正確設定 LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET")

# ✅ 初始化 LINE Bot 與 Flask App
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = Flask(__name__)

# ✅ 靜態圖片目錄：/Cards/xxx.jpg
@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

# ✅ 首頁健康檢查
@app.route("/", methods=["GET"])
def index():
    return "🌙 Dream Oracle LINE BOT 正在運行中！"

# ✅ Webhook 路由
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    app.logger.info("=== LINE Webhook Received ===")
    app.logger.info("Signature: " + signature)
    app.logger.info("Body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("⚠️ Invalid signature.")
        abort(400)
    except Exception as e:
        app.logger.error(f"🔥 其他錯誤：{e}")
        abort(500)

    return "OK"

# ✅ 處理 LINE 訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print("👤 使用者 ID：", user_id)

    try:
        if user_input.startswith("新增 "):
            parts = user_input.split()
            if len(parts) == 3 and parts[2].startswith("http"):
                keyword = parts[1]
                url = parts[2]
                path = "dream_links.json"
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    data = {}

                data[keyword] = url
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                reply_text = f"✅ 已成功新增：{keyword}\n🔗 {url}"
                messages = [TextMessage(text=reply_text)]
            else:
                reply_text = "⚠️ 請使用正確格式：\n新增 關鍵字 網址\n範例：新增 蛇 https://www.golla.tw/..."
                messages = [TextMessage(text=reply_text)]

        elif user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="👋 感謝使用 Dream Oracle，再會～")]

        else:
            result = process_dream(user_input, user_id=user_id)
            reply_text = result.get("text", "⚠️ 系統錯誤，請稍後再試")
            image_filename = result.get("image")

            messages = [TextMessage(text=reply_text)]

            if image_filename:  # ✅ 若有圖片才加上圖片訊息
                image_url = f"https://dream-oracle.onrender.com/Cards/{image_filename}"

                if "⚠️ 尚未支援此夢境" in reply_text:
                    messages.append(TextMessage(text="我們會儘快補上這個夢境的解析，感謝你的提醒 🙇"))

                messages.append(
                    ImageMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url
                    )
                )

        # ✅ 回覆訊息
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )

    except Exception as e:
        print(f"[ERROR] 回傳訊息失敗：{e}")

# ✅ 開發測試本地啟動
if __name__ == "__main__":
    app.run(port=5001)
