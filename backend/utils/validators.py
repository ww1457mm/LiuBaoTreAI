import re
import unicodedata
from typing import Any, Optional


MAX_QUESTION_LEN = 500
MAX_NAME_LEN = 64
MAX_CONTENT_LEN = 10000


def sanitize_string(value: Any, max_len: int = 200) -> str:
    """清理字符串输入：去空格、控制字符，截断长度。"""
    if value is None:
        return ""
    s = str(value).strip()
    s = "".join(
        c for c in s if unicodedata.category(c)[0] != "C" or c in ("\n", "\t")
    )
    return s[:max_len]


def sanitize_question(value: Any) -> str:
    """清理用户问题输入。"""
    return sanitize_string(value, max_len=MAX_QUESTION_LEN)


def sanitize_nickname(value: Any) -> str:
    """清理昵称输入。"""
    raw = sanitize_string(value, max_len=MAX_NAME_LEN)
    raw = re.sub(r'[<>\"\'`\\;]', "", raw)
    return raw


def sanitize_openid(value: Any) -> Optional[str]:
    """验证并清理 openid。"""
    if value is None:
        return None
    raw = sanitize_string(value, max_len=128)
    if not raw:
        return None
    if len(raw) < 4:
        return None
    return raw


def sanitize_task_type(value: Any) -> str:
    """验证并清理任务类型。"""
    if value == "disease":
        return "disease"
    return "disease"


def sanitize_fav_type(value: Any) -> str:
    """验证并清理收藏类型。"""
    allowed = {"knowledge", "qa", "recognition"}
    if value in allowed:
        return value
    return "knowledge"


def sanitize_page_params(page: Any, page_size: Any, max_page_size: int = 100) -> tuple[int, int]:
    """规范化分页参数。"""
    try:
        p = max(1, int(page))
    except (TypeError, ValueError):
        p = 1
    try:
        ps = max(1, min(int(page_size), max_page_size))
    except (TypeError, ValueError):
        ps = 20
    return p, ps


def sanitize_html(value: Any, max_len: int = 500) -> str:
    """清理可能含 HTML/脚本的内容，去除标签和危险字符。"""
    if value is None:
        return ""
    s = str(value).strip()
    # 去除 HTML 标签
    s = re.sub(r"<[^>]+>", "", s)
    # 去除危险字符
    s = re.sub(r"[<>\"'`\\;]", "", s)
    s = "".join(
        c for c in s if unicodedata.category(c)[0] != "C" or c in ("\n", "\t")
    )
    return s[:max_len]
