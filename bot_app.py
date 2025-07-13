from flask import Flask, request, abort, send_from_directory
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from dream_core import process_dream
from datetime import datetime
from pathlib import Path
import os
import json

# ✅ 載入 .env 檔案
load_dotenv(dotenv_path=Path(".env"))

# ✅ 引入 Gemini SDK 並設定 API KEY
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ 載入環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DEVELOPER_USER_ID = os.getenv("DEVELOPER_USER_ID")

# ✅ 確認必要變數
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET]):
    raise EnvironmentError("❌ 請確認 .env 是否正確設定 LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET")

# ✅ 初始化 Flask 與 LINE Bot
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = Flask(__name__)

# ✅ 靜態圖片服務
@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

# ✅ 健康檢查
@app.route("/", methods=["GET"])
def index():
    return "\ud83c\udf19 Dream Oracle LINE BOT \u6b63\u5728\u904b\u884c\u4e2d\uff01"

# ✅ LINE Webhook 路由
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
        app.logger.warning("\u26a0\ufe0f Invalid signature.")
        abort(400)
    except Exception as e:
        app.logger.error(f"\ud83d\udd25 \u5176\u4ed6\u932f\u8aa4\uff1a{e}")
        abort(500)

    return "OK"

# ✅ 分段工具
MAX_LENGTH = 4900

def split_message(text, max_len=MAX_LENGTH):
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

# ✅ 主訊息處理函數
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print("\ud83d\udc64 \u4f7f\u7528\u8005 ID\uff1a", user_id)

    try:
        if user_input.startswith("\u65b0\u589e "):
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

                reply_text = f"\u2705 \u5df2\u6210\u529f\u65b0\u589e\uff1a{keyword}\n\ud83d\udd17 {url}"
                messages = [TextMessage(text=reply_text)]
            else:
                reply_text = "\u26a0\ufe0f \u8acb\u4f7f\u7528\u6b63\u78ba\u683c\u5f0f\uff1a\n\u65b0\u589e \u95dc\u9375\u5b57 \u7db2\u5740\n\u7bc4\u4f8b\uff1a\u65b0\u589e \u86c7 https://www.golla.tw/..."
                messages = [TextMessage(text=reply_text)]

        elif user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="\ud83d\udc4b \u611f\u8b1d\u4f7f\u7528 Dream Oracle\uff0c\u518d\u6703\u301c")] 

        else:
            result = process_dream(user_input, user_id=user_id)
            reply_text = result.get("text", "\u26a0\ufe0f \u7cfb\u7d71\u932f\u8aa4\uff0c\u8acb\u7a0d\u5f8c\u518d\u8a66")

            # ✅ Gemini 補充夢境說明
            try:
                gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                gemini_response = gemini_model.generate_content(
                    f"\u4f7f\u7528\u6eab\u67d4\u3001\u7642\u7652\u7684\u8a9e\u6c23\uff0c\u88dc\u5145\u5922\u5883\u300c{user_input}\u300d\u7684\u5fc3\u7406\u8c61\u5fb5\u610f\u7fa9\uff0c\u9650\u5236\u5728 3 \u884c\u5167\u3002"
                )
                supplement = gemini_response.text.strip()

                if supplement:
                    reply_text += f"\n\n\ud83d\udca1 Gemini \u88dc\u5145\uff1a\n{supplement}"

            except Exception as ge:
                print(f"[Gemini Error] {ge}")

            # ✅ 建立分段訊息
            messages = [TextMessage(text=part) for part in split_message(reply_text)]

            image_filename = result.get("image")
            if image_filename:
                image_url = f"https://dream-oracle.onrender.com/Cards/{image_filename}"

                if "\u26a0\ufe0f \u5c1a\u672a\u652f\u63f4\u6b64\u5922\u5883" in reply_text:
                    messages.append(TextMessage(text="\u6211\u5011\u6703\u511f\u5feb\u88dc\u4e0a\u9019\u500b\u5922\u5883\u7684\u89e3\u6790\uff0c\u611f\u8b1d\u4f60\u7684\u63d0\u9192 \ud83d\ude47"))

                messages.append(ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))

                messages.append(TextMessage(
                    text="\u8acb\u518d\u8f38\u5165\u4e0b\u4e00\u500b\u5922\u5883\u95dc\u9375\u5b57\u5427\uff0c\u6211\u5011\u6703\u70ba\u4f60\u6301\u7e8c\u6307\u5c0e\u3002\n\ud83c\udf1f Dream Oracle \u8207\u4f60\u4e00\u8d77\u63a2\u7d22\u5922\u5883\u8207\u60c5\u7dd2 \ud83c\udf19"
                ))

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
        print(f"[ERROR] \u56de\u50b3\u8a0a\u606f\u5931\u6557\uff1a{e}")

# ✅ 提供 log 查詢
@app.route("/get-missing-log", methods=["GET"])
def get_missing_log():
    log_path = Path(__file__).parent / "missing_keywords.log"
    if not log_path.exists():
        return "\u26a0\ufe0f Log \u6a94\u6848\u4e0d\u5b58\u5728", 404
    with log_path.open("r", encoding="utf-8") as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

# ✅ 本機啟動
if __name__ == "__main__":
    app.run(port=5001)