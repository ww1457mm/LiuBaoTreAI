import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))

SYSTEM_PROMPT = """你是六堡茶领域的专业智能助手。六堡茶是广西梧州特色黑茶，核心产区包括苍梧县六堡镇等地。
请用简洁、准确的中文回答用户问题。六堡茶基础常识可以直接回答；若提供了参考资料，请优先依据参考资料作答；若问题超出资料和常识范围，不要编造不确定信息。"""
