# main.py
from dream_core import process_dream

def main():
    print("🌙 歡迎來到 Dream Oracle 解夢卡牌系統")
    print("========================================\n")

    while True:
        keyword = input("🔍 請輸入你夢到的關鍵字（例如：火、蛇、牙齒）\n👉 或輸入 q 離開：").strip()
        if keyword.lower() in ["q", "quit", "exit"]:
            print("\n👋 感謝使用，再會～\n")
            break

        result = process_dream(keyword)

        print("\n📜 解夢結果如下：")
        print("──────────────────────────────────────")
        print(result["text"])
        print("🖼️ 對應圖片檔名：", result["image"])
        print("──────────────────────────────────────")
        print("🔁 你可以再輸入其他夢境關鍵字，或輸入 q 離開\n")

if __name__ == "__main__":
    main()

from database import write_to_postgres

# 呼叫範例
write_to_postgres("夢見火", "恐懼")
