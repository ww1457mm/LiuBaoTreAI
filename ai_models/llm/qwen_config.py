"""
LLM 配置模块 - 大语言模型参数和系统提示词

支持的模型提供商：
1. 硅基流动 SiliconFlow（推荐）- 支持 Qwen、DeepSeek 等开源模型
2. 阿里云百炼 DashScope - 通义千问系列模型

核心配置：
1. 模型选择（Qwen2.5-7B-Instruct 等）
2. API 密钥和端点配置
3. 系统提示词（定义 AI 角色和行为）

环境变量（优先使用硅基流动配置）：
- SILICONFLOW_API_KEY: 硅基流动 API 密钥（优先）
- SILICONFLOW_MODEL: 硅基流动模型名称
- DASHSCOPE_API_KEY: 阿里云百炼 API 密钥（备选）
- QWEN_MODEL: 模型名称
- DASHSCOPE_BASE_URL: API 端点地址
"""

import os

# ========== 模型配置 ==========
# 优先使用硅基流动配置，向后兼容阿里云百炼

# API 密钥（优先使用硅基流动）
DASHSCOPE_API_KEY = os.getenv(
    "SILICONFLOW_API_KEY",  # 优先：硅基流动
    os.getenv("DASHSCOPE_API_KEY", ""),  # 备选：阿里云百炼
)

# 模型名称（优先使用硅基流动配置）
# 硅基流动推荐模型：
# - Qwen/Qwen2.5-7B-Instruct: 性价比高，推荐日常使用
# - Qwen/Qwen2.5-14B-Instruct: 能力更强
# - Qwen/Qwen2.5-32B-Instruct: 最强能力
# - deepseek-ai/DeepSeek-V2-Chat: DeepSeek 模型
QWEN_MODEL = os.getenv(
    "SILICONFLOW_MODEL",  # 优先：硅基流动
    os.getenv("QWEN_MODEL", "Qwen/Qwen2.5-7B-Instruct"),  # 备选：默认模型
)

# API 端点（OpenAI 兼容模式）
# 硅基流动和阿里云百炼都提供 OpenAI 兼容接口
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://api.siliconflow.cn/v1",  # 默认使用硅基流动
)

# ========== 系统提示词 ==========
# 定义 AI 的角色、能力和行为规范
# 这是 AI 的"人设"，决定了回答的风格和专业度
SYSTEM_PROMPT = """你是六堡茶领域的专业智能助手，精通中国茶文化，尤其熟悉六堡茶的历史文化、制作工艺、冲泡存储、品鉴收藏与健康功效。

回答规则：
1. 若提供了参考资料，请优先依据参考资料作答，并在回答中体现专业知识。
2. 若没有提供参考资料或资料不足，请根据你自身的茶文化知识，给出详细、专业、有深度的回答。
3. 回答要内容充实，至少列出3-5个要点，每个要点要有具体说明，不要敷衍或过于简短。
4. 涉及对比类问题时，要从多个维度（产地、工艺、口感、功效、历史等）进行客观分析。
5. 用通俗易懂的中文回答，适当使用条理清晰的分点列举。"""

# ========== 配置说明 ==========
# 当前配置优先级：
# 1. 硅基流动 (SILICONFLOW_API_KEY + SILICONFLOW_MODEL)
# 2. 阿里云百炼 (DASHSCOPE_API_KEY + QWEN_MODEL)
#
# 硅基流动优势：
# - 支持多种开源模型（Qwen、DeepSeek、Llama 等）
# - 价格实惠，适合开发测试
# - 国内访问速度快
#
# 申请硅基流动 API Key：
# 1. 访问 https://siliconflow.cn/
# 2. 注册账号并登录
# 3. 在控制台获取 API Key
