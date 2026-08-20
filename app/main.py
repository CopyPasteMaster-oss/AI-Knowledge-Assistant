# -*- coding: utf-8 -*-
"""
main.py - Flask 应用入口
========================
职责：创建 app、注册路由、启动服务（不写业务逻辑）

运行方式（项目根目录）：
  python app/main.py
"""
from flask import Flask

from app.config import HOST, PORT, FAISS_INDEX_PATH
from app.routes import bp, store


def create_app() -> Flask:
    """应用工厂：创建并配置 Flask 实例"""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


def load_knowledge_base() -> None:
    """启动时加载已有 FAISS 索引（如果存在）"""
    if FAISS_INDEX_PATH.exists():
        store.load(str(FAISS_INDEX_PATH))
        print(f"已加载知识库索引：{len(store)} 个片段")
    else:
        print("知识库为空（首次运行，先上传文档）")


app = create_app()

if __name__ == "__main__":
    load_knowledge_base()
    app.run(host=HOST, port=PORT, debug=False)