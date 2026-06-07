import random
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.quiz import QuizRecord
from backend.models.user import User
from backend.utils.validators import sanitize_openid

router = APIRouter(prefix="/api", tags=["quiz"])

# ========== 六堡茶知识题库 ==========
QUESTIONS = [
    {"id": 1, "q": "六堡茶属于哪类茶？", "options": ["绿茶", "红茶", "黑茶", "白茶"], "answer": 2, "explain": "六堡茶是中国黑茶代表之一，产于广西梧州。"},
    {"id": 2, "q": "六堡茶最显著的香气特征是？", "options": ["兰花香", "槟榔香", "蜜香", "奶香"], "answer": 1, "explain": "槟榔香是六堡茶最具辨识度的香气特征。"},
    {"id": 3, "q": "六堡茶的产地在哪里？", "options": ["云南普洱", "广西梧州", "福建武夷", "湖南安化"], "answer": 1, "explain": "六堡茶产于广西壮族自治区梧州市苍梧县六堡镇。"},
    {"id": 4, "q": "六堡茶的'四绝'是指？", "options": ["红浓陈醇", "色香味形", "甘润厚滑", "香清甘活"], "answer": 0, "explain": "六堡茶以'红、浓、陈、醇'四绝著称。"},
    {"id": 5, "q": "六堡茶渥堆发酵的目的是？", "options": ["杀青止酵", "促进后发酵", "去除水分", "增加香气"], "answer": 1, "explain": "渥堆是六堡茶后发酵的核心工序，产生独特风味。"},
    {"id": 6, "q": "以下哪种不是六堡茶的制作工序？", "options": ["杀青", "揉捻", "渥堆", "摇青"], "answer": 3, "explain": "摇青是乌龙茶的工序，六堡茶不需要摇青。"},
    {"id": 7, "q": "六堡茶适合用什么温度的水冲泡？", "options": ["80°C", "85°C", "90°C", "100°C"], "answer": 3, "explain": "六堡茶是黑茶，适合用沸水（100°C）冲泡。"},
    {"id": 8, "q": "六堡茶的'陈化'是指？", "options": ["高温烘焙", "自然存放转化", "冷冻保存", "真空包装"], "answer": 1, "explain": "陈化是六堡茶在适宜环境中自然存放、缓慢转化的过程。"},
    {"id": 9, "q": "六堡茶的历史大约有多少年？", "options": ["500年", "1000年", "1500年", "2000年"], "answer": 2, "explain": "六堡茶有1500多年的历史，是中国历史名茶。"},
    {"id": 10, "q": "六堡茶的'茶船古道'是指？", "options": ["陆上丝绸之路", "茶叶水运外销路线", "茶马古道", "京杭大运河"], "answer": 1, "explain": "茶船古道是六堡茶经西江水路运往东南亚的贸易路线。"},
    {"id": 11, "q": "以下哪个不是六堡茶的核心产区？", "options": ["六堡镇", "狮寨镇", "武夷山", "梨木镇"], "answer": 2, "explain": "武夷山在福建，是岩茶产区，不是六堡茶产区。"},
    {"id": 12, "q": "六堡茶的茶汤颜色应该是？", "options": ["浅绿", "金黄", "红浓", "橙红"], "answer": 2, "explain": "六堡茶茶汤以红浓为佳，体现后发酵茶的特征。"},
    {"id": 13, "q": "六堡茶属于后发酵茶，对吗？", "options": ["对", "错"], "answer": 0, "explain": "六堡茶是后发酵茶，通过渥堆和陈化完成发酵。"},
    {"id": 14, "q": "六堡茶可以用紫砂壶冲泡，对吗？", "options": ["对", "错"], "answer": 0, "explain": "紫砂壶透气性好，非常适合冲泡六堡茶等黑茶。"},
    {"id": 15, "q": "六堡茶的采摘标准以什么为佳？", "options": ["一芽一叶", "单片叶", "老叶", "茶籽"], "answer": 0, "explain": "六堡茶以一芽一叶或一芽二叶为采摘标准。"},
    {"id": 16, "q": "六堡茶的杀青温度大约是？", "options": ["100-120°C", "150-170°C", "180-200°C", "220-250°C"], "answer": 2, "explain": "六堡茶杀青温度约180-200°C，快速钝化酶活性。"},
    {"id": 17, "q": "六堡茶的渥堆发酵时间一般为？", "options": ["1-3天", "7-15天", "30-50天", "3-6个月"], "answer": 2, "explain": "六堡茶渥堆发酵一般需要30-50天。"},
    {"id": 18, "q": "六堡茶的'党校茶'是指什么工艺？", "options": ["渥堆发酵", "松柴明火烘焙", "日晒干燥", "蒸汽杀青"], "answer": 1, "explain": "党校茶是传统松柴明火烘焙工艺的六堡茶。"},
    {"id": 19, "q": "六堡茶具有什么保健功效？", "options": ["降脂养胃", "提神醒脑", "清热解毒", "以上都是"], "answer": 3, "explain": "六堡茶具有降脂、养胃、提神等多种保健功效。"},
    {"id": 20, "q": "六堡茶的最佳存放条件是？", "options": ["高温潮湿", "阴凉干燥通风", "冰箱冷藏", "密封暴晒"], "answer": 1, "explain": "六堡茶需要在阴凉、干燥、通风、无异味的环境中存放。"},
    {"id": 21, "q": "六堡茶的'干仓'和'湿仓'哪个更好？", "options": ["干仓", "湿仓", "一样好", "都不好"], "answer": 0, "explain": "干仓存储的六堡茶转化更自然，品质更稳定。"},
    {"id": 22, "q": "六堡茶的揉捻工序在什么时候进行？", "options": ["杀青前", "杀青后趁热", "干燥后", "陈化后"], "answer": 1, "explain": "六堡茶在杀青后趁热进行揉捻，使茶汁外溢。"},
    {"id": 23, "q": "以下哪种不是六堡茶的品质特征？", "options": ["红浓陈醇", "槟榔香", "回甘持久", "兰花香"], "answer": 3, "explain": "兰花香不是六堡茶的典型特征，槟榔香才是。"},
    {"id": 24, "q": "六堡茶的年份越久越好，对吗？", "options": ["对", "不一定", "错", "看品牌"], "answer": 1, "explain": "不是越久越好，存储条件不当会导致品质下降。"},
    {"id": 25, "q": "六堡茶的'毛茶'是指？", "options": ["成品茶", "初制完成的茶", "茶树鲜叶", "陈年老茶"], "answer": 1, "explain": "毛茶是初制工艺完成后、未经精制的半成品茶。"},
    {"id": 26, "q": "六堡茶的精制工艺包括哪些步骤？", "options": ["渥堆、复揉、干燥", "杀青、揉捻", "萎凋、干燥", "发酵、烘焙"], "answer": 0, "explain": "精制工艺包括渥堆发酵、复揉整形、干燥三步。"},
    {"id": 27, "q": "六堡茶适合什么季节饮用？", "options": ["只适合夏天", "只适合冬天", "四季皆宜", "只适合秋天"], "answer": 2, "explain": "六堡茶性温和，四季皆宜，尤其适合秋冬暖胃。"},
    {"id": 28, "q": "六堡茶的'金花'是指什么？", "options": ["茶叶上的金色绒毛", "冠突散囊菌", "茶叶变质", "添加的香料"], "answer": 1, "explain": "金花是冠突散囊菌，是一种有益菌，说明茶品质好。"},
    {"id": 29, "q": "六堡茶的投茶量一般为？", "options": ["3克/150ml", "7克/150ml", "15克/150ml", "20克/150ml"], "answer": 1, "explain": "六堡茶一般投茶7克左右配150ml盖碗或壶。"},
    {"id": 30, "q": "六堡茶的第一泡应该怎么处理？", "options": ["直接喝", "倒掉（洗茶）", "泡久一点", "加糖"], "answer": 1, "explain": "第一泡通常倒掉，称为洗茶或醒茶，去除杂质并唤醒茶叶。"},
    {"id": 31, "q": "六堡茶的'槟榔香'是怎么产生的？", "options": ["添加槟榔", "渥堆和陈化过程中自然形成", "烘焙产生", "品种自带"], "answer": 1, "explain": "槟榔香是六堡茶在渥堆发酵和长期陈化过程中自然形成的。"},
    {"id": 32, "q": "六堡茶可以煮着喝吗？", "options": ["可以", "不可以", "只有老茶可以", "只有新茶可以"], "answer": 0, "explain": "六堡茶可以煮饮，尤其是陈年老茶，煮饮更显醇厚。"},
    {"id": 33, "q": "苍梧县属于哪个市？", "options": ["南宁市", "柳州市", "梧州市", "桂林市"], "answer": 2, "explain": "苍梧县隶属于广西梧州市，是六堡茶核心产区。"},
    {"id": 34, "q": "六堡茶的'复揉'在什么工序之后？", "options": ["杀青", "渥堆发酵", "干燥", "陈化"], "answer": 1, "explain": "复揉在渥堆发酵之后进行，进一步紧结条索。"},
    {"id": 35, "q": "以下哪种茶与六堡茶同属黑茶？", "options": ["龙井", "铁观音", "普洱熟茶", "大红袍"], "answer": 2, "explain": "普洱熟茶和六堡茶都属于黑茶类，都是后发酵茶。"},
    {"id": 36, "q": "六堡茶的'陈香'是指什么类型的香气？", "options": ["花果香", "木质香/药香", "奶香", "海苔香"], "answer": 1, "explain": "陈香是六堡茶陈化后产生的木质香、药香等复合香气。"},
    {"id": 37, "q": "六堡茶的茶多酚含量与绿茶相比？", "options": ["更高", "差不多", "更低", "无法比较"], "answer": 2, "explain": "六堡茶经过发酵，茶多酚被氧化转化，含量低于绿茶。"},
    {"id": 38, "q": "六堡茶适合搭配什么食物？", "options": ["甜点", "油腻食物", "海鲜", "以上都可以"], "answer": 3, "explain": "六堡茶解腻消食，搭配各种食物都合适。"},
    {"id": 39, "q": "六堡茶的'社前茶'是指什么？", "options": ["春分前采的茶", "清明前采的茶", "谷雨前采的茶", "立夏前采的茶"], "answer": 0, "explain": "社前茶指春社（春分前后）之前采摘的六堡茶，品质最佳。"},
    {"id": 40, "q": "六堡茶的英文名是？", "options": ["Pu-erh Tea", "Liu Bao Tea", "Oolong Tea", "Black Tea"], "answer": 1, "explain": "六堡茶的英文名是 Liu Bao Tea 或 Liubao Tea。"},
    {"id": 41, "q": "六堡茶在清代是贡茶吗？", "options": ["是", "不是", "只有慈禧喝过", "不确定"], "answer": 0, "explain": "清代嘉庆年间，六堡茶被列为全国名茶，是贡茶之一。"},
    {"id": 42, "q": "六堡茶的'霜降茶'是指什么季节采的？", "options": ["春季", "夏季", "秋季", "冬季"], "answer": 2, "explain": "霜降茶指霜降节气前后采摘的秋茶。"},
    {"id": 43, "q": "六堡茶的茶叶外形特征是？", "options": ["卷曲成球", "条索紧结", "扁平光滑", "针形挺直"], "answer": 1, "explain": "六堡茶条索紧结，色泽黑褐光润。"},
    {"id": 44, "q": "六堡茶的'桂青种'是指？", "options": ["茶树品种", "制作工艺", "产区名称", "品牌名"], "answer": 0, "explain": "桂青种是六堡茶的主要茶树品种之一。"},
    {"id": 45, "q": "六堡茶的'茶气'是指什么？", "options": ["茶的温度", "茶的气味", "饮后身体的温热感", "茶的浓度"], "answer": 2, "explain": "茶气指饮茶后身体感受到的温热、发汗等体感反应。"},
    {"id": 46, "q": "六堡茶的'老茶婆'是指？", "options": ["老年女性茶农", "粗老叶片制作的茶", "陈年普洱", "茶饼"], "answer": 1, "explain": "老茶婆是用较粗老的叶片制作的六堡茶，口感甘甜。"},
    {"id": 47, "q": "六堡茶的冲泡器具首选是？", "options": ["玻璃杯", "紫砂壶/盖碗", "塑料杯", "纸杯"], "answer": 1, "explain": "紫砂壶或盖碗最适合冲泡六堡茶，能充分展现茶韵。"},
    {"id": 48, "q": "六堡茶的'冷水发酵'是指？", "options": ["用冷水冲泡", "自然陈化过程", "一种新工艺", "冰镇饮用"], "answer": 2, "explain": "冷水发酵是一种较新的六堡茶加工工艺。"},
    {"id": 49, "q": "六堡茶的'三鹤'品牌来自哪里？", "options": ["梧州茶厂", "苍梧六堡", "南宁茶厂", "桂林茶厂"], "answer": 0, "explain": "三鹤牌是梧州茶厂的知名品牌。"},
    {"id": 50, "q": "六堡茶的'中茶'品牌属于哪家公司？", "options": ["中粮集团", "中国茶叶", "天福茗茶", "大益集团"], "answer": 1, "explain": "中茶牌属于中国茶叶有限公司。"},
]


@router.get("/quiz/questions")
def get_questions(count: int = Query(10, ge=5, le=20)):
    """获取随机题目"""
    selected = random.sample(QUESTIONS, min(count, len(QUESTIONS)))
    # 返回时不包含答案，但包含解析
    return {
        "code": 0,
        "data": [
            {"id": q["id"], "q": q["q"], "options": q["options"], "explain": q["explain"]}
            for q in selected
        ],
    }


class QuizSubmit(BaseModel):
    openid: str
    answers: list  # [{id: 1, answer: 2}, ...]


class QuizJudge(BaseModel):
    answers: list  # [{id: 1, answer: 2}, ...]  单题或多题判分，无需登录


@router.post("/quiz/judge")
def judge_quiz(body: QuizJudge, db: Session = Depends(get_db)):
    """单题判分（用于答题过程，不保存记录）"""
    q_map = {q["id"]: q for q in QUESTIONS}
    results = []
    for ans in body.answers:
        q = q_map.get(ans.get("id"))
        if not q:
            continue
        try:
            user_ans = int(ans.get("answer"))
        except (TypeError, ValueError):
            user_ans = None
        correct = user_ans == int(q["answer"])
        results.append({
            "id": q["id"],
            "q": q["q"],
            "your_answer": ans.get("answer"),
            "correct_answer": q["answer"],
            "correct": correct,
            "explain": q["explain"],
            "options": q["options"],
        })
    return {"code": 0, "data": {"results": results}}


@router.post("/quiz/submit")
def submit_quiz(body: QuizSubmit, db: Session = Depends(get_db)):
    """提交答案并判分"""
    openid = sanitize_openid(body.openid) or body.openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    # 构建题目索引
    q_map = {q["id"]: q for q in QUESTIONS}

    results = []
    score = 0
    for ans in body.answers:
        q = q_map.get(ans.get("id"))
        if not q:
            continue
        try:
            user_ans = int(ans.get("answer"))
        except (TypeError, ValueError):
            user_ans = None
        correct = user_ans == int(q["answer"])
        if correct:
            score += 1
        results.append({
            "id": q["id"],
            "q": q["q"],
            "your_answer": ans.get("answer"),
            "correct_answer": q["answer"],
            "correct": correct,
            "explain": q["explain"],
            "options": q["options"],
        })

    total = len(results)

    # 保存记录
    record = QuizRecord(user_id=user.id, score=score, total=total)
    db.add(record)
    db.commit()

    # 评级
    if total == 0:
        grade = "未知"
    elif score / total >= 0.9:
        grade = "茶圣"
    elif score / total >= 0.7:
        grade = "茶师"
    elif score / total >= 0.5:
        grade = "茶友"
    else:
        grade = "茶小白"

    return {
        "code": 0,
        "data": {
            "score": score,
            "total": total,
            "grade": grade,
            "results": results,
        },
    }


@router.get("/quiz/history")
def quiz_history(
    openid: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取答题历史"""
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    offset = (page - 1) * page_size
    query = db.query(QuizRecord).filter(QuizRecord.user_id == user.id).order_by(QuizRecord.create_time.desc())
    total = query.count()
    items = query.offset(offset).limit(page_size).all()
    return {
        "code": 0,
        "data": [
            {"id": r.id, "score": r.score, "total": r.total, "create_time": r.create_time.isoformat() if r.create_time else ""}
            for r in items
        ],
        "total": total,
    }
