import jieba
from collections import Counter

def map_emotion(text):
    """
    根據夢境解析文字進行情緒判定：
    - 使用 jieba 分詞建立詞頻表
    - 對照多組情緒關鍵字分類
    """

    if text.startswith("⚠️"):
        return "未知"

    words = jieba.lcut(text)
    freq = Counter(words)

    # 關鍵詞分類（可擴充）
    emotion_keywords = {
        "焦慮": ["掉牙", "迷路", "追趕", "失敗", "遲到", "焦慮", "緊張"],
        "恐懼": ["蛇", "黑暗", "鬼", "墜落", "死亡", "害怕"],
        "快樂": ["飛翔", "陽光", "花", "笑", "海邊", "快樂", "開心", "幸福"],
        "悲傷": ["哭", "下雨", "失戀", "分手", "孤單", "悲傷", "痛苦", "失落"],
        "驚奇": ["中獎", "懷孕", "變身", "寶藏", "意外"],
        "愛": ["擁抱", "親吻", "戀人", "家人", "朋友"]
    }

    # 詞頻分析後比對分類
    for word, _ in freq.most_common():
        for emotion, keywords in emotion_keywords.items():
            if word in keywords:
                return emotion

    return "未知"
