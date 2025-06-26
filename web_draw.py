# 在 Flask 頁面顯示卡牌圖片
from flask import Flask, request, render_template_string, send_from_directory
from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from oracle_engine import draw_card

app = Flask(__name__)

# 首頁：顯示輸入表單
@app.route('/')
def home():
    return '''
    <h2>🌙 Dream Oracle 解夢卡牌</h2>
    <form action="/result" method="post">
        請輸入夢境關鍵詞：<input name="keyword" required>
        <input type="submit" value="開始解夢">
    </form>
    '''

# 解夢結果頁：解釋 + 卡牌圖 + 情緒
@app.route('/result', methods=['POST'])
def result():
    keyword = request.form['keyword'].strip()
    dream_text = get_dream_interpretation(keyword)
    emotion = map_emotion(dream_text)
    card = draw_card(emotion)

    html = f"""
    <html>
    <head><title>Dream Oracle 結果</title></head>
    <body style="text-align:center; font-family:sans-serif;">
        <h2>你夢到了「{keyword}」</h2>
        <p><strong>🔍 解夢內容：</strong>{dream_text}</p>
        <p><strong>🎭 分析情緒：</strong>{emotion}</p>
        <h3>你抽到的卡牌是：{card['title']}</h3>
        <p>{card['message']}</p>
        <img src="/cards/{card['image']}" alt="{card['title']}" style="max-width:300px; margin-top:20px;">
        <br><br><a href="/">🔁 再抽一次</a>
    </body>
    </html>
    """
    return html

# 讀取 cards/ 資料夾內的圖片
@app.route('/cards/<filename>')
def serve_card_image(filename):
    return send_from_directory('cards', filename)

if __name__ == '__main__':
    app.run(debug=True)
