from flask import Flask, request, abort, send_from_directory, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai
import psycopg2
import os
import traceback
from dream_core import process_dream
from database import write_to_postgres, init_db, get_all_logs  # ✅ 正確引入所有功能

# === ✅ 初始化環境變數與 API 金鑰 ===
load_dotenv(dotenv_path=Path(".env"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")

if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, DATABASE_URL]):
    raise EnvironmentError("❌ 請確認 .env 中設定了必要的變數")

# === ✅ 初始化 Flask 與 LINE Webhook Handler ===
app = Flask(__name__)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === ✅ 啟動時建立資料表 ===
init_db()

# === ✅ 卡牌圖片靜態路由 ===
@app.route("/Cards/<path:filename>")
def serve_card_image(filename):
    return send_from_directory("Cards", filename)

# === ✅ 健康檢查路由 ===
@app.route("/", methods=["GET"])
def index():
    return "🌙 Dream Oracle LINE BOT 正在運行中！"

# === ✅ LINE Webhook 接收端點 ===
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
        traceback.print_exc()
        app.logger.error(f"🔥 其他錯誤：{str(e)}")
        abort(500)

    return "OK"

# === ✅ 處理使用者文字訊息 ===

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print("👤 使用者 ID：", user_id)

    try:
        if user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="👋 感謝使用 Dream Oracle，再會～")]
        else:
            result = process_dream(user_input)
            print("[DEBUG] 處理結果：", result)

            # ✅ ✅ ✅ 加入這行，將使用者輸入與情緒寫入資料庫
            write_to_postgres(user_input, result["emotion"])

            reply_text = (
                f"🔍 解夢關鍵字：{user_input}\n"
                f"🧠 解夢結果：\n{result['dream_text']}\n\n"
                f"🌝 情緒判定：{result['emotion']}\n"
                f"🃏 命定卡牌：「{result['title']}」\n"
                f"👉 {result['message']}"
            )

            messages = [TextMessage(text=reply_text[i:i + 4900]) for i in range(0, len(reply_text), 4900)]

            if result.get("image"):
                image_url = f"https://dream-oracle.onrender.com/Cards/{result['image']}"
                messages.append(ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))

            messages.append(TextMessage(text="請再輸入下一個夢境關鍵字吧，我們會為你持續指徑\n🌟 Dream Oracle 與你一起探索夢境與情緒 🌙"))

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )

    except Exception as e:
        traceback.print_exc()
        print(f"[ERROR] 回傳訊息失敗：{str(e)}")


# === ✅ [查詢記錄] 顯示已寫入的夢境資料 ===
@app.route("/logs", methods=["GET"])
def view_logs():
    try:
        rows = get_all_logs()
        html = "<h2>使用者輸入記錄</h2><ul>"
        for row in rows:
            html += f"<li>🌙 關鍵字: {row[0]} ｜情緒: {row[1]} ｜時間: {row[2]}</li>"
        html += "</ul>"
        return html
    except Exception as e:
        traceback.print_exc()
        return f"❌ 查詢失敗：{str(e)}", 500

# === ✅ [測試寫入] 手動觸發寫入一筆紀錄 ===
@app.route("/log/<keyword>/<emotion>")
def log(keyword, emotion):
    try:
        write_to_postgres(keyword, emotion)
        return "✅ 寫入成功"
    except Exception as e:
        traceback.print_exc()
        return f"❌ 寫入失敗：{str(e)}", 500

# === ✅ 本地啟動（Render 上不會執行這段） ===
if __name__ == "__main__":
    app.run(port=5001)
