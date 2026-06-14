"""
文本向量化模块 - 将文本转换为数值向量，用于语义搜索

核心功能：
1. 调用 SiliconFlow API 获取文本的向量表示（嵌入向量）
2. 无 API 时使用本地哈希生成伪向量作为降级方案
3. 内置缓存机制避免重复请求

技术细节：
- 使用 BAAI/bge-large-zh-v1.5 模型，输出 1024 维向量
- 向量用于 FAISS 索引，实现高效的相似度搜索
"""

from __future__ import annotations

import os
import time
from typing import List

import numpy as np

# ========== 配置项 ==========
# SiliconFlow API 密钥，从环境变量读取
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

# SiliconFlow 嵌入向量 API 地址
SILICONFLOW_EMBED_URL = os.getenv(
    "SILICONFLOW_EMBED_URL",
    "https://api.siliconflow.cn/v1/embeddings",
)

# 使用的嵌入模型名称（中文优化的大模型）
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-large-zh-v1.5")

# 向量维度，bge-large-zh-v1.5 输出 1024 维
# 本地伪向量必须保持一致，避免与 FAISS 索引维度冲突
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))

# 内存缓存：文本 -> 向量的映射，避免重复计算
_EMBED_CACHE: dict[str, np.ndarray] = {}

# API 请求最大重试次数
_MAX_RETRIES = 2


def embed_dim() -> int:
    """获取向量维度"""
    return EMBED_DIM


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    批量将文本转换为向量

    参数:
        texts: 文本列表

    返回:
        numpy 数组，形状为 (len(texts), EMBED_DIM)

    工作流程:
    1. 检查缓存，跳过已有的文本
    2. 对未缓存的文本调用 API 获取向量
    3. 将结果存入缓存并返回
    """
    if not texts:
        return np.zeros((0, EMBED_DIM), dtype=np.float32)

    # 找出未缓存的文本
    uncached = [t for t in texts if t not in _EMBED_CACHE]

    # 如果有未缓存的文本，请求 API 获取向量
    if uncached:
        vectors = _request_embeddings(uncached)
        # 将新获取的向量存入缓存
        for text, vec in zip(uncached, vectors):
            _EMBED_CACHE[text] = vec

    # 从缓存中按顺序取出所有向量，堆叠成矩阵返回
    return np.stack([_EMBED_CACHE[t] for t in texts]).astype(np.float32)


def _request_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    调用 SiliconFlow API 获取文本向量

    参数:
        texts: 待向量化的文本列表

    返回:
        向量列表，每个元素是一个 numpy 数组

    降级策略:
    - 如果没有 API 密钥，直接使用本地哈希生成伪向量
    - 如果 API 调用失败，重试最多 _MAX_RETRIES 次
    - 重试间隔递增（1秒、2秒）
    - 所有重试失败后降级为本地伪向量
    """
    # 如果有 API 密钥，尝试调用远程 API
    if SILICONFLOW_API_KEY:
        for attempt in range(_MAX_RETRIES):
            try:
                import httpx

                # 发送 POST 请求到嵌入向量 API
                resp = httpx.post(
                    SILICONFLOW_EMBED_URL,
                    headers={"Authorization": f"Bearer {SILICONFLOW_API_KEY}"},
                    json={"model": EMBED_MODEL, "input": texts},
                    timeout=30.0,
                )
                resp.raise_for_status()

                # 解析响应，提取向量数据
                data = resp.json()["data"]
                # 按原始顺序排序（API 可能乱序返回）
                data.sort(key=lambda x: x["index"])
                return [np.array(item["embedding"], dtype=np.float32) for item in data]

            except Exception:
                # 请求失败，等待后重试
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                break

    # 降级：使用本地哈希生成伪向量
    return [_local_hash_embedding(t) for t in texts]


def _local_hash_embedding(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    """
    无 API 时的确定性伪向量生成

    参数:
        text: 输入文本
        dim: 向量维度，默认 1024

    返回:
        归一化的伪向量

    原理:
    - 使用文本的哈希值作为随机种子
    - 生成固定维度的随机向量
    - 归一化为单位向量

    优点:
    - 相同文本总是生成相同向量（确定性）
    - 保证 FAISS 索引可以正常运行
    - 无需外部 API 依赖

    注意:
    - 这不是真正的语义向量，无法捕捉文本含义
    - 仅用于开发测试或 API 不可用时的降级
    """
    # 使用文本哈希作为随机种子，保证相同文本生成相同向量
    rng = np.random.default_rng(abs(hash(text)) % (2**32))

    # 生成标准正态分布的随机向量
    vec = rng.standard_normal(dim).astype(np.float32)

    # L2 归一化，使其成为单位向量
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm

    return vec
