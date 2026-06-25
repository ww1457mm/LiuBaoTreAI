from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai_models.llm.ollama_client import chat_completion

router = APIRouter(prefix="/api", tags=["recommend"])

TASTE_MAP = {"light": "清淡鲜爽", "medium": "适中均衡", "strong": "浓郁醇厚"}
BUDGET_MAP = {"low": "50元以下/斤", "mid": "50-200元/斤", "high": "200-500元/斤", "premium": "500元以上/斤"}
PURPOSE_MAP = {"daily": "日常饮用", "collect": "收藏投资", "gift": "送礼"}
HEALTH_MAP = {"lipid": "降脂减肥", "stomach": "暖胃养胃", "antioxidant": "抗氧化", "none": "无特殊需求"}


class RecommendRequest(BaseModel):
    taste: str = Field(default="medium")
    budget: str = Field(default="mid")
    purpose: str = Field(default="daily")
    health: str = Field(default="none")
    season: str = Field(default="")


@router.post("/recommend")
def recommend_tea(body: RecommendRequest):
    """AI 个性化推荐"""
    taste_desc = TASTE_MAP.get(body.taste, "适中均衡")
    budget_desc = BUDGET_MAP.get(body.budget, "50-200元/斤")
    purpose_desc = PURPOSE_MAP.get(body.purpose, "日常饮用")
    health_desc = HEALTH_MAP.get(body.health, "无特殊需求")

    prompt = f"""你是一位六堡茶推荐专家。请根据以下用户偏好，推荐 3 款适合的六堡茶。

口味偏好：{taste_desc}
预算范围：{budget_desc}
饮用目的：{purpose_desc}
健康需求：{health_desc}
当前季节：{body.season or '不限'}

请按以下 JSON 格式返回推荐结果（只返回 JSON，不要其他文字）：
{{
  "recommendations": [
    {{
      "name": "茶名",
      "type": "类型（生茶/熟茶/老茶等）",
      "price": "参考价格区间",
      "reason": "推荐理由（50字以内）",
      "brew_tip": "冲泡建议（30字以内）",
      "match_score": 匹配度(1-100)
    }}
  ],
  "summary": "总体建议（50字以内）"
}}"""

    try:
        result = chat_completion(prompt)
        import json
        start = result.find('{')
        end = result.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(result[start:end])
            return {"code": 0, "data": data}
        else:
            return {"code": 0, "data": {"summary": result}}
    except Exception:
        return {"code": 0, "data": {
            "recommendations": [
                {
                    "name": "三年陈六堡熟茶",
                    "type": "熟茶",
                    "price": "80-150元/斤",
                    "reason": "性价比高，口感醇和，适合日常饮用。",
                    "brew_tip": "100°C沸水，7克/150ml，首泡15秒",
                    "match_score": 85
                },
                {
                    "name": "五年陈社前茶",
                    "type": "生茶",
                    "price": "200-400元/斤",
                    "reason": "回甘好，有收藏价值，越陈越香。",
                    "brew_tip": "95°C水温，8克/150ml，首泡10秒",
                    "match_score": 78
                },
                {
                    "name": "十年陈老茶婆",
                    "type": "老茶",
                    "price": "300-600元/斤",
                    "reason": "陈香显著，汤感醇厚，暖胃效果好。",
                    "brew_tip": "100°C沸水煮饮更佳",
                    "match_score": 72
                }
            ],
            "summary": "根据您的偏好，建议从熟茶入手，逐步尝试老茶。"
        }}
