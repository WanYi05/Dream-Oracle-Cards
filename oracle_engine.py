import random
import csv

def load_cards():
    """
    從 card_data.csv 中讀取所有卡牌資料，依情緒分類
    """
    cards_by_emotion = {}
    with open("emotion_cards_full.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            emotion = row["emotion"]
            if emotion not in cards_by_emotion:
                cards_by_emotion[emotion] = []
            cards_by_emotion[emotion].append({
                "title": row["title"],
                "message": row["message"]
            })
    return cards_by_emotion

def draw_card(emotion):
    """
    根據情緒抽出一張卡牌，若情緒未知則隨機抽一張
    """
    all_cards = load_cards()
    if emotion in all_cards:
        return random.choice(all_cards[emotion])
    else:
        # 萬一情緒未知，從全部卡牌隨機抽
        flat_list = [card for cards in all_cards.values() for card in cards]
        return random.choice(flat_list)
 
