from dream_parser import get_dream_interpretation
from emotion_mapper import map_emotion
from oracle_engine import draw_card
from utils import save_result

def main():
    print("🌙 歡迎來到 Dream Oracle 解夢卡牌系統")

    while True:
        keyword = input("請輸入你夢到的關鍵字（例如：火、蛇、牙齒....），或輸入 q 離開：").strip()
        if keyword.lower() in ["q", "quit", "exit"]:
            print("👋 感謝使用，再會～")
            break

        print("\n🔍 正在查詢夢境解析...\n")
        dream_text = get_dream_interpretation(keyword)

        print("🧠 解夢結果：")
        print(dream_text)

        print("\n🎭 分析夢境情緒...")
        if dream_text.startswith("⚠️"):
            emotion = "未知"
        else:
            emotion = map_emotion(dream_text)
        print(f"➡️ 判定情緒為：{emotion}")

        print("\n🃏 為你抽取命定卡牌...\n")
        card = draw_card(emotion)
        print(f"🔮 卡牌建議：「{card['title']}」\n👉 {card['message']}")

        print("\n💾 儲存結果中...")
        save_result(keyword, dream_text, emotion, card)

        print("\n✅ 全部完成！感謝使用 Dream Oracle ✨\n")
        print("🔁 你可以再輸入其他夢境關鍵字，或輸入 q 離開\n")

if __name__ == "__main__":
    main()