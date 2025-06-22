# build_dream_links.py
import requests
from bs4 import BeautifulSoup
import json

def get_all_dream_links(base_url="https://www.golla.tw/"):
    headers = {"User-Agent": "Mozilla/5.0"}
    dream_links = {}

    try:
        resp = requests.get(base_url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            print("❌ 主頁載入失敗")
            return {}

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            # 過濾出像 /dongwu/she.html 這樣的有效連結
            if href.endswith(".html") and text and not href.startswith("http"):
                full_url = base_url.rstrip("/") + "/" + href.lstrip("/")
                if text not in dream_links:
                    dream_links[text] = full_url

        return dream_links

    except Exception as e:
        print(f"⚠️ 發生錯誤：{e}")
        return {}

if __name__ == "__main__":
    links = get_all_dream_links()
    with open("dream_links.json", "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
    print(f"✅ 共建立 {len(links)} 筆夢境關鍵詞連結")
