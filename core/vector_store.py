# -*- coding: utf-8 -*-
"""
vector_store.py - FAISS 向量库模块
==================================
存储文档向量 + 相似度检索（Top-K 最近邻）。

设计要点：
1. IndexFlatIP（内积索引）配合归一化向量 = 余弦相似度排序（与 embedding.py 衔接）
2. documents 列表与向量一一对应（向量 id -> 原文），检索结果可直接返回文本
3. 支持持久化：save/load 到 data/vector_db/
"""
import faiss
import numpy as np


class VectorStore:
    """基于 FAISS 的向量库：添加向量 + Top-K 相似度检索"""

    def __init__(self, dim: int = 512):
        self.dim = dim
        # 内积索引：归一化向量下等价于余弦相似度
        self.index = faiss.IndexFlatIP(dim)
        self.documents = []  # 与向量一一对应的文本（索引 id -> 原文）

    def add(self, texts: list, vectors) -> None:
        """批量添加文档文本 + 对应向量

        参数:
            texts:   文本列表（与 vectors 顺序一致）
            vectors: 向量矩阵 shape=(n, dim)
        """
        v = np.ascontiguousarray(vectors, dtype=np.float32)  # FAISS 要求 float32 连续内存
        if v.ndim != 2 or v.shape[1] != self.dim:
            raise ValueError(f"向量形状错误: {v.shape}，应为 (n, {self.dim})")
        if len(texts) != v.shape[0]:
            raise ValueError(f"文本数 {len(texts)} 与向量数 {v.shape[0]} 不一致")
        self.index.add(v)
        self.documents.extend(texts)

    def search(self, query_vector, top_k: int = 3) -> list:
        """检索与查询向量最相似的 Top-K 条

        参数:
            query_vector: 查询向量 shape=(dim,)
            top_k:        返回条数
        返回:
            [{"id": int, "score": float, "text": str}, ...] 按相似度降序
        """
        q = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        scores, ids = self.index.search(q, top_k)

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:  # FAISS 空索引/不足时返回 -1
                continue
            i = int(idx)
            results.append({"id": i, "score": float(score), "text": self.documents[i]})
        return results

    def save(self, path: str) -> None:
        """保存索引到文件（FAISS 格式 .faiss）"""
        faiss.write_index(self.index, path)

    def load(self, path: str) -> None:
        """从文件加载索引（documents 由调用方按相同顺序恢复）"""
        self.index = faiss.read_index(path)

    def __len__(self):
        return self.index.ntotal


if __name__ == "__main__":
    # 自测：python vector_store.py
    store = VectorStore(dim=8)
    # 随机造 3 条"向量"模拟文档
    rng = np.random.default_rng(42)
    vecs = rng.random((3, 8))
    store.add(["文档一：考勤制度", "文档二：休假流程", "文档三：报销规定"], vecs)
    q = vecs[1]  # 用"文档二"的向量查询，最相似应是它自己
    print("检索结果:", store.search(q, top_k=2))