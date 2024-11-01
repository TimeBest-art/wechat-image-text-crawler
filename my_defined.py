
import re
# 移除 emoji 的正则表达式
def remove_emojis(text):
    return re.sub(r'[^\w\s,.!?-]', '', text)