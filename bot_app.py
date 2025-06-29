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
import os
import json

from dream_core import process_dream  # ✅ 解夢邏輯核心

# ✅ 載入環境變數
load_dotenv()
configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
DEVELOPER_USER_ID = os.getenv("DEVELOPER_USER_ID")  # ✅ 開發者 LINE ID

# ✅ 初始化 Flask App
app = Flask(__name__)

# ✅ 公開圖片路由：讓 /Cards/<filename> 能正確顯示
@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

# ✅ 加入首頁路由，避免 404
@app.route("/", methods=["GET"])
def index():
    return "🌙 Dream Oracle LINE BOT 正在運行中！"

# ✅ LINE Webhook 接收點
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
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
        app.logger.error(f"🔥 Other error: {e}")
        abort(500)

    return 'OK'

# ✅ 處理 LINE 的文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    print("👤 使用者 ID：", event.source.user_id)
    user_input = event.message.text.strip()

    # ✅ [新增指令]：格式為「新增 關鍵字 網址」
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
            reply_text = "⚠️ 格式錯誤，請使用：\n新增 關鍵字 網址\n範例：新增 蛇 https://www.golla.tw/..."
            messages = [TextMessage(text=reply_text)]

    elif user_input.lower() in ["q", "quit", "exit"]:
        reply_text = "👋 感謝使用 Dream Oracle，再會～"
        messages = [TextMessage(text=reply_text)]

    else:
        user_id = event.source.user_id
        result = process_dream(user_input, user_id=user_id)
        reply_text = result["text"]
        image_filename = result["image"]

        # ✅ 查無資料 → 寫入 log 並推播給開發者
        if result["text"].startswith("🔍") and "⚠️ 尚未支援此夢境" in result["text"]:
            # ➕ 寫入 log（加上錯誤處理）
            try:
                with open("missing_keywords.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()} - 未支援夢境關鍵字：{user_input}\n")
            except Exception as e:
                print(f"[WARNING] 無法寫入 missing_keywords.log：{e}")

            # ➕ 推播給開發者
            try:
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.push_message(
                        to=DEVELOPER_USER_ID,
                        messages=[TextMessage(text=f"🚨 有人查了未支援的夢境關鍵字：{user_input}")]
                    )
            except Exception as e:
                print(f"[WARNING] 無法推播通知開發者：{e}")

            # 回覆使用者（不附圖片）
            messages = [
                TextMessage(text=reply_text),
                TextMessage(text="我們會儘快補上這個夢境的解析，感謝你的提醒 🙇")
            ]
        else:
            # ✅ 正常情況 → 傳文字 + 圖片
            image_url = f"https://dream-oracle.onrender.com/Cards/{image_filename}"
            messages = [
                TextMessage(text=reply_text),
                ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                )
            ]

    # ✅ 統一回覆訊息（加入 try，避免 webhook fail）
    try:
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

# ✅ 本地測試啟動
if __name__ == "__main__":
    app.run(port=5001)
