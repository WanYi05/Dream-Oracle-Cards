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
from dream_core import process_dream
import os
import google.generativeai as genai

# ✅ 載入 .env 環境變數
load_dotenv(dotenv_path=Path(".env"))

# ✅ 設定 Gemini API 金鑰
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ 讀取 LINE 機密資訊
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET]):
    raise EnvironmentError("❌ 請確認 .env 是否正確設定 LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET")

# ✅ 建立 Flask 應用與 LINE Handler
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = Flask(__name__)

# ✅ 卡牌圖片靜態路由
@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

# ✅ 健康檢查
@app.route("/", methods=["GET"])
def index():
    return "🌙 Dream Oracle LINE BOT 正在運行中！"

# ✅ LINE Webhook 接收端點
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
        import traceback
        traceback.print_exc()
        app.logger.error(f"🔥 其他錯誤：{str(e).encode('utf-8', 'ignore').decode('utf-8')}")
        abort(500)

    return "OK"

# ✅ 使用者訊息處理邏輯
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print("👤 使用者 ID：", user_id)

    try:
        if user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="👋 感謝使用 Dream Oracle，再會～")]
        else:
            # ✅ 呼叫核心邏輯分析夢境
            result = process_dream(user_input)
            print("[DEBUG] 處理結果：", result)

            reply_text = f"💡 Gemini 解夢補充：\n{result['text']}"


            messages = []
            # 🔹 分段回覆避免超過 LINE 單則字數限制
            max_length = 4900
            for i in range(0, len(reply_text), max_length):
                messages.append(TextMessage(text=reply_text[i:i+max_length]))

            # ✅ 若有圖片則加入圖片訊息（Render 上請確認 domain）
            if result.get("image"):
                image_url = f"https://dream-oracle.onrender.com/Cards/{result['image']}"
                messages.append(ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))

            messages.append(TextMessage(text="請再輸入下一個夢境關鍵字吧，我們會為你持續指引。\n🌟 Dream Oracle 與你一起探索夢境與情緒 🌙"))

        # ✅ 發送回覆訊息
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] 回傳訊息失敗：{str(e).encode('utf-8', 'ignore').decode('utf-8')}")

# ✅ 本地開發使用
if __name__ == "__main__":
    app.run(port=5001)
