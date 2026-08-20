# -*- coding: utf-8 -*-
"""
routes.py - HTTP 接口层
=======================
只做三件事：收请求 → 调 core 干活 → 包装响应。
业务逻辑一律在 core/，本文件不写任何算法。

接口：
  POST /upload  上传文档（PDF/TXT/MD/DOCX）→ 解析切片向量化入知识库
  POST /chat    问答：检索 + DeepSeek 生成
  GET  /history 查询历史记录
"""
import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify

from app.config import DOCUMENTS_DIR, FAISS_INDEX_PATH, TOP_K, CHUNK_SIZE, CHUNK_OVERLAP
from core.document_loader import load_document
from core.splitter import split_text
from core.embedding import embed_texts
from core.vector_store import VectorStore
from core.retriever import retrieve
from core.llm import ask

bp = Blueprint("api", __name__)

# 进程级单例：知识库（启动时加载已有索引）
store = VectorStore(dim=512)
_history = []  # 简化版历史（内存保存，重启清空）


@bp.post("/upload")
def upload():
    """上传文档 → 解析 → 切片 → 向量化 → 入库"""
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"error": "缺少文件字段 'file'"}), 400

    # 保存到 documents 目录（防路径穿越：只用文件名）
    filename = Path(file.filename).name
    save_path = DOCUMENTS_DIR / f"{uuid.uuid4().hex[:8]}_{filename}"
    file.save(str(save_path))

    try:
        text = load_document(str(save_path))          # ① 解析
        chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)  # ② 切片
        if not chunks:
            return jsonify({"error": "文档未提取到有效文本"}), 400
        store.add(chunks, embed_texts(chunks))        # ③ 向量化 + 入库
        store.save(str(FAISS_INDEX_PATH))             # 持久化索引
        return jsonify({"ok": True, "chunks": len(chunks), "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.post("/chat")
def chat():
    """问答：检索最相关片段 → DeepSeek 生成回答"""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "缺少字段 'question'"}), 400

    try:
        hits = retrieve(store, question, top_k=TOP_K)          # ① 检索
        answer = ask(question, [h["text"] for h in hits])      # ② 生成
        _history.append({"question": question, "answer": answer})
        return jsonify({
            "answer": answer,
            "sources": [{"score": round(h["score"], 3), "text": h["text"][:100]} for h in hits],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/history")
def history():
    """返回问答历史（内存版）"""
    return jsonify({"history": _history[-20:]})


@bp.get("/health")
def health():
    """健康检查"""
    return jsonify({"ok": True, "documents": len(store)})