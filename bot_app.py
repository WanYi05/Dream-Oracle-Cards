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
        if user_input.startswith("新增 "):
            parts = user_input.split()
            if len(parts) == 3 and parts[2].startswith("http"):
                keyword, url = parts[1], parts[2]
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
                messages = [TextMessage(text="⚠️ 請使用正確格式：\n新增 關鍵字 網址\n範例：新增 蛇 https://www.golla.tw/...")]

        elif user_input.lower() in ["q", "quit", "exit"]:
            messages = [TextMessage(text="👋 感謝使用 Dream Oracle，再會～")]

        else:
            result = process_dream(user_input, user_id=user_id)
            reply_text = result.get("text", "⚠️ 系統錯誤，請稍後再試")

            # ✅ Gemini 補充夢境說明
            try:
                gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                gemini_response = gemini_model.generate_content(
                    f"使用溫柔、療癒的語氣，補充夢境「{user_input}」的心理象徵意義，限制在 3 行內。"
                )
                supplement = gemini_response.text.strip()
                supplement = supplement.encode("utf-8", "ignore").decode("utf-8")
                if supplement:
                    reply_text += f"\n\n💡 Gemini 補充：\n{supplement}"
            except Exception as ge:
                print(f"[Gemini Error] {str(ge).encode('utf-8', 'ignore').decode('utf-8')}")

            # ✅ 處理圖片與回覆文字
            image_filename = result.get("image")
            messages = []
            max_length = 4900
            for i in range(0, len(reply_text), max_length):
                messages.append(TextMessage(text=reply_text[i:i+max_length]))

            if image_filename:
                image_url = f"https://dream-oracle.onrender.com/Cards/{image_filename}"
                if "⚠️ 尚未支援此夢境" in reply_text:
                    messages.append(TextMessage(text="我們會儘快補上這個夢境的解析，感謝你的提醒 🙇"))
                messages.append(ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))
                messages.append(TextMessage(text="請再輸入下一個夢境關鍵字吧，我們會為你持續指引。\n🌟 Dream Oracle 與你一起探索夢境與情緒 🌙"))

        # ✅ 回覆使用者
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

@app.route("/get-missing-log", methods=["GET"])
def get_missing_log():
    log_path = Path(__file__).parent / "missing_keywords.log"
    if not log_path.exists():
        return "⚠️ Log 檔案不存在", 404
    with log_path.open("r", encoding="utf-8") as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(port=5001)