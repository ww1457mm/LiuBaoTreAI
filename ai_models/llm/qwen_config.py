import os

QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

SYSTEM_PROMPT = """你是六堡茶领域的专业智能助手，熟悉六堡茶的历史文化、制作工艺、冲泡存储、品鉴收藏与健康功效。
请用简洁、准确的中文回答用户问题。若提供了参考资料，请优先依据参考资料作答，并在回答中体现专业知识。"""
