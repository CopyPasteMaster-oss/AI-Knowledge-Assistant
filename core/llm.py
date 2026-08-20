# -*- coding: utf-8 -*-
"""
llm.py - 大模型调用模块（DeepSeek API）
======================================
把"检索到的资料 + 问题"组装成 Prompt，调用 DeepSeek 生成有依据的回答。

设计要点：
1. API key 从项目根 .env 读取（key 不入库，.gitignore 已排除）
2. system prompt 明确"只根据资料回答，不编造"——抑制幻觉
3. temperature 低（0.3）：忠实于资料，减少随机发挥
"""
from pathlib import Path

import requests

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
TEMPERATURE = 0.3  # 低温度：忠实于检索资料，减少幻觉

_SYSTEM_PROMPT = (
    "你是企业知识库智能助手。请严格根据提供的参考资料回答问题；"
    "如果参考资料中没有相关信息，请明确回答'资料中未找到相关信息'，不要编造。"
)


def _load_api_key() -> str:
    """从项目根 .env 读取 DeepSeek API key"""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            key = line.split("=", 1)[1].strip()
            if key:
                return key
    raise RuntimeError(".env 中缺少 DEEPSEEK_API_KEY，请检查项目根目录 .env 文件")


def build_user_prompt(question: str, contexts: list) -> str:
    """组装 user prompt：参考资料 + 问题（RAG 的核心拼接逻辑）"""
    refs = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(contexts))
    return f"参考资料：\n{refs}\n\n问题：{question}"


def ask(question: str, contexts: list) -> str:
    """RAG 问答：给定问题和检索到的资料片段，返回模型回答"""
    user_prompt = build_user_prompt(question, contexts)
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {_load_api_key()}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": TEMPERATURE,
            "stream": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]