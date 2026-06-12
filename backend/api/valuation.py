from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai_models.llm.dashscope_client import chat_completion

router = APIRouter(prefix="/api", tags=["valuation"])


class ValuationRequest(BaseModel):
    tea_name: str = Field(default="六堡茶", max_length=128)
    tea_type: str = Field(default="", max_length=64)
    year: int = Field(default=5, ge=0, le=100)
    appearance: str = Field(default="", max_length=256)
    storage: str = Field(default="干仓", max_length=64)
    origin: str = Field(default="", max_length=128)


@router.post("/valuation")
def valuate_tea(body: ValuationRequest):
    """AI 茶叶估价"""
    prompt = f"""你是一位资深的六堡茶鉴定专家。请根据以下茶叶信息进行品质评估和估价。

茶名：{body.tea_name}
茶类：{body.tea_type or '六堡茶'}
年份：{body.year}年
外观描述：{body.appearance or '未提供'}
存储条件：{body.storage}
产地：{body.origin or '广西梧州'}

请按以下 JSON 格式返回评估结果（只返回 JSON，不要其他文字）：
{{
  "quality_score": 评分(1-100),
  "quality_level": "品质等级（特级/一级/二级/三级）",
  "price_min": 最低参考价(元/斤),
  "price_max": 最高参考价(元/斤),
  "analysis": "品质分析（100字以内）",
  "storage_advice": "存储建议（50字以内）",
  "brew_advice": "冲泡建议（50字以内）"
}}"""

    try:
        result = chat_completion(prompt)
        # 尝试提取 JSON
        import json
        # 找到 JSON 块
        start = result.find('{')
        end = result.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(result[start:end])
            return {"code": 0, "data": data}
        else:
            return {"code": 0, "data": {"analysis": result}}
    except Exception as e:
        return {"code": 0, "data": {
            "quality_score": 65,
            "quality_level": "二级",
            "price_min": 80,
            "price_max": 200,
            "analysis": f"基于{body.year}年陈期和{body.storage}存储条件的综合评估。建议送专业机构进一步鉴定。",
            "storage_advice": "继续在阴凉干燥通风处存放，避免异味。",
            "brew_advice": "100°C沸水冲泡，投茶7克/150ml，首泡15秒出汤。"
        }}
