import csv
import random

def load_cards():
    cards_by_emotion = {}
    with open("emotion_cards_full.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            emotion = row["emotion"]
            if emotion not in cards_by_emotion:
                cards_by_emotion[emotion] = []
            cards_by_emotion[emotion].append({
                "title": row["title"],
                "message": row["message"],
                "image": row["image"]
            })
    return cards_by_emotion

def draw_card(emotion):
    all_cards = load_cards()
    if emotion in all_cards:
        card = random.choice(all_cards[emotion])  # ✅ 一整行抽出
    else:
        flat_list = [card for cards in all_cards.values() for card in cards]
        card = random.choice(flat_list)

    return {
        "title": card["title"],
        "message": card["message"],
        "image": card["image"]
    }
