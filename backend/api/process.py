from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["process"])


# 六堡茶加工工艺流程数据
PROCESS_STAGES = [
    {
        "id": 1,
        "phase": "初制工艺",
        "name": "采摘",
        "emoji": "🌿",
        "duration": "清明前后",
        "description": "采摘六堡茶鲜叶，以一芽一叶或一芽二叶为佳，此时茶叶嫩度适中，内含物质丰富。",
        "tips": "阴雨天不采露水叶，采摘时间宜选晴天上午露水干后进行。",
        "key_point": "原料品质决定成茶品质，采摘标准是关键第一步",
    },
    {
        "id": 2,
        "phase": "初制工艺",
        "name": "杀青",
        "emoji": "🔥",
        "duration": "180-200°C，3-5分钟",
        "description": "通过高温快速钝化多酚氧化酶，制止茶叶氧化，保持绿茶特色的关键工序。传统用铁锅手工杀青，现代多用滚筒杀青机。",
        "tips": "温度不够则杀青不足导致红梗，温度过高则焦叶。",
        "key_point": "高温快出，投叶均匀，杀透杀匀",
    },
    {
        "id": 3,
        "phase": "初制工艺",
        "name": "揉捻",
        "emoji": "🖐️",
        "duration": "15-30分钟",
        "description": "趁热揉捻，使茶叶细胞破碎，茶汁外溢，卷紧条索。初揉轻压，后加重压，分次进行，避免茶汁流失过多。",
        "tips": "揉捻不足条索松散，揉捻过度则茶汤发黑。",
        "key_point": "趁热轻揉，逐步加压，短时多次",
    },
    {
        "id": 4,
        "phase": "精制工艺",
        "name": "渥堆发酵",
        "emoji": "💧",
        "duration": "30-50天",
        "description": "六堡茶品质形成的关键工序。将揉捻叶洒水堆放，利用湿热作用促进茶叶内含物质转化，产生独特槟榔香和陈香。",
        "tips": "渥堆时控制水分、温度和厚度，翻堆要均匀适度。",
        "key_point": "渥堆是六堡茶后发酵的核心，决定品质风味",
    },
    {
        "id": 5,
        "phase": "精制工艺",
        "name": "复揉",
        "emoji": "🔄",
        "duration": "10-20分钟",
        "description": "渥堆发酵完成后，进行复揉整形。进一步紧结条索，整理外形，使茶叶形状更加美观匀整。",
        "tips": "复揉力度适中，保持条索完整。",
        "key_point": "渥堆适度后立即复揉，防止堆温过高酸馊",
    },
    {
        "id": 6,
        "phase": "精制工艺",
        "name": "干燥",
        "emoji": "☀️",
        "duration": "木架烘焙，分毛火、足火",
        "description": "传统采用松柴明火烘焙，称党校茶。毛火快速蒸发水分，足火低温慢烘，形成六堡茶独特的松烟香和醇厚口感。",
        "tips": "忌高温急烘，防止外干内湿，影响后期转化。",
        "key_point": "低温慢烘，忌暴晒，保留酶活性利于后期陈化",
    },
    {
        "id": 7,
        "phase": "陈化存储",
        "name": "陈化",
        "emoji": "🪵",
        "duration": "1年以上，越陈越佳",
        "description": "制成毛茶后需在清洁、通风、干燥、无异味的环境中自然存放。随时间推移，茶叶苦涩味降低，汤色转红，口感更加醇滑，形成陈、醇、红、浓的品质特征。",
        "tips": "忌与异味物品同存，注意防潮。",
        "key_point": "干仓存储，自然转化，时间是最好的工艺",
    },
]

PROCESS_PHASES = [
    {
        "id": 1,
        "name": "初制工艺",
        "description": "从鲜叶到毛茶",
        "color": "#4a8c3f",
    },
    {
        "id": 2,
        "name": "精制工艺",
        "description": "毛茶到成品",
        "color": "#e67e22",
    },
    {
        "id": 3,
        "name": "陈化存储",
        "description": "时间赋予品质",
        "color": "#c0392b",
    },
]


@router.get("/process")
def get_process():
    """获取六堡茶加工工艺流程"""
    return {
        "code": 0,
        "data": {
            "phases": PROCESS_PHASES,
            "stages": PROCESS_STAGES,
        },
    }
