# main.py
from dream_core import process_dream

def main():
    print("🌙 歡迎來到 Dream Oracle 解夢卡牌系統")

    while True:
        keyword = input("請輸入你夢到的關鍵字（例如：火、蛇、牙齒....），或輸入 q 離開：").strip()
        if keyword.lower() in ["q", "quit", "exit"]:
            print("👋 感謝使用，再會～")
            break

        result = process_dream(keyword)
        print(result)
        print("\n🔁 你可以再輸入其他夢境關鍵字，或輸入 q 離開\n")

if __name__ == "__main__":
    main()