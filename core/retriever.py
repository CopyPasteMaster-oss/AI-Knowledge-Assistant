# -*- coding: utf-8 -*-
"""
retriever.py - 检索模块
=======================
查询文本 -> embedding -> 向量库 Top-K 检索（RAG 的"查资料"环节）

与 vector_store 的分工：
- vector_store: 只管"向量进/出 FAISS"（存储 + 搜索原语）
- retriever:    把"文本查询"变成"向量查询"并返回结果（业务层）
"""
from core.embedding import embed_query
from core.vector_store import VectorStore


def retrieve(store: VectorStore, question: str, top_k: int = 3) -> list:
    """检索与问题最相关的 Top-K 文本片段

    参数:
        store:    已建好索引的向量库
        question: 用户问题（纯文本）
        top_k:    返回片段数
    返回:
        [{"id": int, "score": float, "text": str}, ...] 按相似度降序
    """
    q_vec = embed_query(question)          # 查询向量（与文档同一个模型！）
    return store.search(q_vec, top_k=top_k)