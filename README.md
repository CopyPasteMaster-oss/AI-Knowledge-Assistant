# AI Knowledge Assistant · 企业知识库智能问答系统

基于 **RAG（检索增强生成）** 架构的企业知识库智能问答系统：上传企业文档（PDF / TXT / Markdown / Word）→ 系统自动解析、切片、向量化并建立知识库 → 用户提问时先检索最相关的内容，再由大模型生成**有依据的回答**，解决大模型不了解企业私有知识、容易"幻觉"的问题。

## 🛠️ 技术栈

Python | Flask | LangChain | BGE Embedding | FAISS | DeepSeek API

## 🏗️ 项目结构

```
AI-Knowledge-Assistant/
├── app/          # Web 层（Flask 入口 / 路由 / 配置）
├── core/         # 核心引擎（文档解析 / 切片 / 向量化 / 检索 / LLM）
├── data/
│   ├── documents/  # 用户上传的文档
│   └── vector_db/  # FAISS 向量库索引
├── frontend/     # 前端页面（聊天界面 / 文件上传）
└── screenshots/  # 运行截图
```

## 🚧 开发状态

- [x] Stage 1：项目初始化（目录结构 + 本 README）
- [x] Stage 2：文档处理（PDF/TXT/MD/Word 解析 + 文本切片）✅ `core/document_loader.py` `core/splitter.py`
- [x] Stage 3：Embedding（BGE 中文模型文本向量化）✅ `core/embedding.py`
- [x] Stage 4：FAISS 知识库（向量存储 + Top-K 相似度检索）✅ `core/vector_store.py`
- [ ] Stage 5：RAG 流程（Retriever + Prompt + DeepSeek 调用）
- [ ] Stage 6：Flask 接口（上传 API + 问答 API）
- [ ] Stage 7：Web 页面（聊天 + 上传）
- [ ] Stage 8：项目优化（引用来源 / 多轮对话 / 流式输出）

> 模型文件（BGE）不入库：clone 后按 README 说明下载，或使用 `models/bge-small-zh-v1.5` 本地路径。
