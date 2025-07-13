from dream_core import process_dream

dream_input = "夢見被火追趕"
result = process_dream(dream_input)

print("🔍 解夢關鍵字：", dream_input)
print("💡 Gemini 補充：", result["text"])
print("🎭 情緒判定：", result["emotion"])
print("🃏 命定卡牌：", result["title"])
print("👉 卡牌訊息：", result["message"])
print("🖼 圖片檔名：", result["image"])
