from utils import init_db, save_result

# ✅ 第一次先建立資料庫和資料表
init_db()

# ✅ 模擬一筆資料
keyword = "掉牙"
dream_text = "夢到掉牙，可能表示焦慮或家中有變動。"
emotion = "焦慮"
card = {
    "title": "改變的訊號",
    "message": "勇敢面對轉變，別害怕失去。"
}

# ✅ 儲存進資料庫
save_result(keyword, dream_text, emotion, card)

print("✅ 資料已成功寫入 SQLite 資料庫！")