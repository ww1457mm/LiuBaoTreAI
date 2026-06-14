"""
向量存储模块 - 基于 FAISS 的向量索引和检索系统

核心功能：
1. 从知识库文本文件构建向量索引
2. 提供高效的相似度搜索
3. 自动管理索引的创建、加载和更新

技术架构：
- 使用 FAISS（Facebook AI Similarity Search）进行向量检索
- 向量由 embedding 模块生成（1024 维）
- 使用内积（IP）相似度计算，向量需归一化
- 索引和元数据持久化到本地文件

文件结构：
- faiss.index: FAISS 索引文件
- meta.json: 文本块元数据（标题、内容、来源、分类）
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple

import numpy as np

from ai_models.rag.embedding import embed_texts

# ========== 路径配置 ==========
# 项目根目录（ai_models/rag/ 向上两级）
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 知识库文本文件目录
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"

# 索引文件存储目录
INDEX_DIR = PROJECT_ROOT / "ai_models" / "rag" / "index"

# FAISS 索引文件路径
INDEX_PATH = INDEX_DIR / "faiss.index"

# 元数据文件路径（存储文本块信息）
META_PATH = INDEX_DIR / "meta.json"


class VectorStore:
    """
    向量存储类 - 管理 FAISS 索引和文本块

    属性:
        index: FAISS 索引对象
        chunks: 文本块列表，每个块包含 title/content/source/category
        _index_loaded: 索引是否已加载的标志

    使用方法:
        store = VectorStore()
        store.build_if_needed()  # 首次使用时构建索引
        results = store.search("查询文本", top_k=5)  # 搜索相似文本
    """

    def __init__(self):
        """初始化向量存储，确保索引目录存在"""
        self.index = None  # FAISS 索引对象
        self.chunks: List[dict] = []  # 文本块列表
        self._index_loaded = False  # 索引加载标志

        # 确保索引目录存在
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

    def build_if_needed(self) -> None:
        """
        按需构建索引

        工作流程:
        1. 如果索引已加载，直接返回
        2. 如果索引文件存在且维度匹配，从文件加载
        3. 否则从知识库重新构建索引

        这个方法是幂等的，可以多次调用
        """
        if self._index_loaded:
            return

        # 检查索引文件是否存在
        if INDEX_PATH.exists() and META_PATH.exists():
            try:
                self._load()
                # 验证索引维度是否与当前嵌入模型匹配
                if self._index_matches_embeddings():
                    self._index_loaded = True
                    return
            except Exception:
                pass
            # 索引文件损坏或维度不匹配，删除重建
            self._remove_index_files()

        # 从知识库构建新索引
        self._build_from_knowledge_base()
        self._index_loaded = True

    def _build_from_knowledge_base(self) -> None:
        """
        从知识库文本文件构建向量索引

        处理流程:
        1. 遍历 knowledge_base 目录下所有 .txt 文件
        2. 读取每个文件的内容，提取分类（父目录名）
        3. 将所有文本块向量化
        4. 构建 FAISS 索引并保存

        文本块结构:
        {
            "title": "文件名（不含扩展名）",
            "content": "文件内容",
            "source": "相对于项目根目录的路径",
            "category": "父目录名，如 history/process/brew"
        }
        """
        chunks = []

        # 遍历知识库目录，递归查找所有 .txt 文件
        for txt in KNOWLEDGE_DIR.rglob("*.txt"):
            content = txt.read_text(encoding="utf-8").strip()
            if not content:
                continue

            # 从目录结构提取分类（如 history/process/brew）
            category = txt.parent.name

            chunks.append({
                "title": txt.stem,  # 文件名不含扩展名
                "content": content,
                "source": str(txt.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "category": category,
            })

        if not chunks:
            return

        # 构造向量化文本：标题 + 内容
        texts = [f"{c['title']}\n{c['content']}" for c in chunks]

        try:
            # 调用 embedding 模块获取向量
            vectors = embed_texts(texts)
            self._save_index(vectors, chunks)
        except Exception:
            # 向量化失败时，只保存文本块（无索引）
            self.chunks = chunks

    def _save_index(self, vectors: np.ndarray, chunks: List[dict]) -> None:
        """
        保存向量索引和元数据到文件

        参数:
            vectors: 向量矩阵，形状 (n, dim)
            chunks: 文本块列表

        技术细节:
        - 使用 IndexFlatIP（内积索引），适用于归一化向量
        - 内积相似度等价于余弦相似度（当向量已归一化）
        """
        import faiss

        dim = vectors.shape[1]

        # 创建内积索引（Inner Product）
        # 对于归一化向量，内积 = 余弦相似度
        index = faiss.IndexFlatIP(dim)

        # L2 归一化，使内积计算等价于余弦相似度
        faiss.normalize_L2(vectors)

        # 添加向量到索引
        index.add(vectors)

        # 持久化索引到文件
        faiss.write_index(index, str(INDEX_PATH))

        # 保存元数据（文本块信息）
        META_PATH.write_text(
            json.dumps(chunks, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # 更新内存中的索引和文本块
        self.index = index
        self.chunks = chunks

    def _load(self) -> None:
        """
        从文件加载索引和元数据

        加载内容:
        - faiss.index: FAISS 索引对象
        - meta.json: 文本块列表
        """
        import faiss

        self.index = faiss.read_index(str(INDEX_PATH))
        self.chunks = json.loads(META_PATH.read_text(encoding="utf-8"))

    def _index_matches_embeddings(self) -> bool:
        """
        检查索引维度是否与当前嵌入模型匹配

        返回:
            bool: 维度是否匹配

        用途:
        - 当更换嵌入模型时，旧索引维度可能不匹配
        - 需要重建索引以保证搜索正确性
        """
        if self.index is None or not self.chunks:
            return False

        # 用一个探测文本检查向量维度
        probe = embed_texts(["__dim_check__"])
        return probe.shape[1] == self.index.d

    def _remove_index_files(self) -> None:
        """
        删除索引文件

        使用场景:
        - 索引文件损坏
        - 维度不匹配需要重建
        """
        self.index = None
        self.chunks = []

        for path in (INDEX_PATH, META_PATH):
            try:
                # Python 3.8+ 支持 missing_ok 参数
                path.unlink(missing_ok=True)
            except TypeError:
                # 兼容旧版本 Python
                if path.exists():
                    path.unlink()

    def _rebuild_index(self) -> None:
        """
        强制重建索引

        使用场景:
        - 搜索时发现维度不匹配
        - 知识库内容更新后需要重建
        """
        self._index_loaded = False
        self._remove_index_files()
        self._build_from_knowledge_base()
        self._index_loaded = True

    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        """
        搜索与查询文本最相似的知识块

        参数:
            query: 查询文本
            top_k: 返回结果数量，默认 3

        返回:
            列表，每个元素是 (文本块字典, 相似度分数)
            - 文本块包含 title/content/source/category
            - 相似度分数范围 [-1, 1]，越大越相似（内积）

        搜索流程:
        1. 确保索引已构建
        2. 将查询文本向量化
        3. 检查向量维度是否匹配
        4. 执行 FAISS 搜索
        5. 返回 top_k 个最相似的结果

        异常处理:
        - 索引为空时返回空列表
        - 维度不匹配时自动重建索引
        - FAISS 导入失败时返回空列表
        """
        # 确保索引已构建
        self.build_if_needed()

        if not self.chunks or self.index is None:
            return []

        try:
            import faiss
        except Exception:
            return []

        # 将查询文本向量化
        q = embed_texts([query])

        # 检查向量维度是否与索引匹配
        if q.shape[1] != self.index.d:
            # 维度不匹配，重建索引
            self._rebuild_index()
            if not self.chunks or self.index is None:
                return []
            # 重新向量化（使用新模型的维度）
            q = embed_texts([query])

        # L2 归一化，与索引构建时保持一致
        faiss.normalize_L2(q)

        # 执行搜索：返回相似度分数和索引
        scores, indices = self.index.search(q, min(top_k, len(self.chunks)))

        # 整理搜索结果
        results = []
        for score, idx in zip(scores[0], indices[0]):
            # FAISS 返回 -1 表示无效结果
            if idx < 0:
                continue
            results.append((self.chunks[idx], float(score)))

        return results
