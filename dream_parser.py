import requests
from bs4 import BeautifulSoup
import json
import os
import difflib


def get_dream_interpretation(keyword):
    # 檢查 dream_links.json 是否存在
    if not os.path.exists("dream_links.json"):
        return "⚠️ 找不到 dream_links.json 檔案"

    # 載入夢境對應網址字典
    with open("dream_links.json", "r", encoding="utf-8") as f:
        dream_links = json.load(f)

    # 如果關鍵字不在字典中，嘗試提供相似建議
    if keyword not in dream_links:
        suggestions = difflib.get_close_matches(keyword, dream_links.keys(), n=3, cutoff=0.6)

        if suggestions:
            print(f"⚠️ 沒有找到「{keyword}」的連結")
            print("🧐 您可能想輸入的是：")
            for s in suggestions:
                print(f"👉 {s}")
        else:
            print(f"⚠️ 沒有找到「{keyword}」的連結，也找不到相近關鍵字。")

        add = input("👉 是否要手動新增此關鍵字對應的網址？(y/n)：").strip().lower()
        if add == "y":
            new_url = input("請輸入對應的完整網址（包含 https://）：").strip()
            if not new_url.startswith("http"):
                new_url = "https://" + new_url

            # 加入並存檔
            dream_links[keyword] = new_url
            with open("dream_links.json", "w", encoding="utf-8") as f:
                json.dump(dream_links, f, ensure_ascii=False, indent=2)
            print("✅ 已新增至 dream_links.json")
        else:
            return f"⚠️ 找不到與「{keyword}」相關的夢境解析"

    url = dream_links.get(keyword)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        entry = soup.find("div", id="entrybody")
        if not entry:
            return "⚠️ 找不到夢境內容區塊"

        return entry.get_text(separator="\n", strip=True)

    except Exception as e:
        return f"⚠️ 無法擷取內容：{e}"
