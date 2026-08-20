# -*- coding: utf-8 -*-
"""
embedding.py - 文本向量化模块
================================
用 BGE 中文模型把文本转成向量，供 FAISS 知识库存储与检索。

设计要点：
1. 文档入库和用户提问必须用【同一个模型】——向量坐标系才可比（语义空间一致）
2. 懒加载单例：模型加载慢（约 400MB），只加载一次，后续复用
3. normalize_embeddings=True：向量归一化，余弦相似度计算更稳定
"""
from pathlib import Path

from sentence_transformers import SentenceTransformer

# 中文 embedding 模型（BGE 系列，中文效果好）
# 优先使用本地 models/ 目录（离线可用、加载快）；不存在时回退在线名（自动下载）
_MODEL_LOCAL = Path(__file__).resolve().parent.parent / "models" / "bge-small-zh-v1.5"
MODEL_NAME = str(_MODEL_LOCAL) if _MODEL_LOCAL.exists() else "BAAI/bge-small-zh-v1.5"

_model = None


def get_model():
    """懒加载模型实例（全局只加载一次）"""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list) -> "numpy.ndarray":
    """批量文本 -> 向量矩阵（每行一个文本的向量）

    参数:
        texts: 文本列表（文档切片）
    返回:
        shape=(n, dim) 的归一化向量矩阵
    """
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)


def embed_query(text: str) -> "numpy.ndarray":
    """单条查询文本 -> 向量（和文档用同一个模型！）"""
    return embed_texts([text])[0]


if __name__ == "__main__":
    # 自测：python embedding.py（首次运行会下载模型，约 400MB）
    vecs = embed_texts(["你好世界", "企业知识库"])
    print("向量维度:", vecs.shape)
    q = embed_query("你好")
    print("查询向量维度:", q.shape)