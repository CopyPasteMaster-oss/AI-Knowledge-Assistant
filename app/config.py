# -*- coding: utf-8 -*-
"""
config.py - 应用配置
====================
集中管理路径与常量（改配置只动这一个文件）
"""
from pathlib import Path

# 项目根目录（app/config.py 的上级）
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据目录
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
VECTOR_DB_DIR = BASE_DIR / "data" / "vector_db"
FAISS_INDEX_PATH = VECTOR_DB_DIR / "knowledge_base.faiss"

# RAG 参数
EMBEDDING_DIM = 512        # BGE small 向量维度
CHUNK_SIZE = 400            # 文本切片长度
CHUNK_OVERLAP = 50          # 切片重叠
TOP_K = 3                   # 检索返回片段数

# 服务器
HOST = "127.0.0.1"
PORT = 5000

# 确保目录存在
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
