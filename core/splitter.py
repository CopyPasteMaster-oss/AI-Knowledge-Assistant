# -*- coding: utf-8 -*-
"""
splitter.py - 文本切片模块
===========================
把长文本切成适合向量化/检索的片段（chunk）。
策略：按段落粗切 → 超长段落按句子聚合 → 相邻片段滑窗重叠（防关键句被切碎）

设计要点：
- 切片太大 → 混入无关内容，检索不准；太小 → 语义破碎
- 中文经验值：chunk_size=400 字，overlap=50 字
"""
import re

# 中文/英文句号结尾（保留标点在句尾）
_SENTENCE_END = re.compile(r"(?<=[。！？!?；;])")


def _split_long_paragraph(para: str, chunk_size: int, overlap: int) -> list:
    """把一个超长段落按句子聚合成多个带重叠的片段"""
    sentences = [s.strip() for s in _SENTENCE_END.split(para) if s.strip()]

    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= chunk_size:
            current += sent
        else:
            if current:
                chunks.append(current)
            # 重叠窗口：取上一片尾部 overlap 字续接，保证边界句子不被切断
            current = current[-overlap:] if current else ""
            current += sent
            # 单句超长（无标点长串）：硬切
            while len(current) > chunk_size:
                chunks.append(current[:chunk_size])
                current = current[chunk_size - overlap:]
    if current:
        chunks.append(current)
    return chunks


def split_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    """把文本切成片段列表（段落边界天然成片，超长段落内部滑窗）

    参数:
        text:      原始文本（document_loader 的输出）
        chunk_size: 每片目标长度（字符数），默认 400
        overlap:    相邻片重叠长度，默认 50
    返回:
        list[str] 片段列表（非空）
    """
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]

    chunks = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            chunks.extend(_split_long_paragraph(para, chunk_size, overlap))
    return chunks


if __name__ == "__main__":
    # 自测：python splitter.py
    demo = ("这是第一段。包含多个句子，测试切片效果。" * 30
            + "\n\n"
            + "这是第二段，短段落。")
    parts = split_text(demo)
    print(f"共切成 {len(parts)} 片")
    for i, p in enumerate(parts[:5]):
        print(f"  [{i}] ({len(p)}字) {p[:40]}...")