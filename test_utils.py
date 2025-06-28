from utils import init_db, save_result

init_db()  # 第一次使用時建立資料夾與檔案

save_result(
    keyword="蛇",
    dream_text="夢見蛇代表潛在危險與內在恐懼。",
    emotion="恐懼",
    card={
        "title": "內心的影子",
        "message": "面對恐懼，你才能真正自由。"
    }
)