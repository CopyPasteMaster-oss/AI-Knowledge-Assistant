# -*- coding: utf-8 -*-
"""
document_loader.py - 文档解析模块
=================================
支持格式：PDF / TXT / Markdown / Word
统一接口：load_document(path) -> str
设计原则：所有格式都返回纯文本，对上层（切片/向量化/检索）隐藏格式差异
"""
from pathlib import Path


def _load_pdf(path: Path) -> str:
    """解析 PDF：pymupdf(fitz) 逐页提取文本"""
    import fitz  # pymupdf

    doc = fitz.open(str(path))
    try:
        texts = [page.get_text() for page in doc]
    finally:
        doc.close()
    return "\n".join(texts)


def _load_word(path: Path) -> str:
    """解析 Word：python-docx 提取段落文本"""
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def _load_text(path: Path) -> str:
    """解析 TXT / Markdown：直接读，自动尝试常见编码"""
    for enc in ("utf-8", "gbk", "utf-16"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法解码文件: {path}")


def load_document(path: str) -> str:
    """统一入口：按扩展名分发到对应解析器，返回纯文本

    参数: path - 文件路径
    返回: str - 提取到的纯文本
    异常: ValueError - 不支持的格式 / 空文件
    """
    p = Path(path)
    suffix = p.suffix.lower()

    # 扩展名 -> 解析器 的映射表（加新格式 = 加一行，不需要改调用方）
    loaders = {
        ".pdf": _load_pdf,
        ".txt": _load_text,
        ".md": _load_text,
        ".markdown": _load_text,
        ".docx": _load_word,
        ".doc": _load_word,
    }

    if suffix not in loaders:
        raise ValueError(f"不支持的格式: {suffix}，目前支持: {sorted(loaders)}")

    text = loaders[suffix](p)
    if not text.strip():
        raise ValueError(f"文件内容为空或无法提取文本: {path}")
    return text


if __name__ == "__main__":
    # 自测入口：python document_loader.py <文件路径>
    import sys

    if len(sys.argv) < 2:
        print("用法: python document_loader.py <文件路径>")
        sys.exit(1)
    text = load_document(sys.argv[1])
    print(f"提取到 {len(text)} 字符，前 200 字：\n{text[:200]}")