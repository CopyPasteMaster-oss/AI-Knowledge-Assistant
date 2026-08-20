# -*- coding: utf-8 -*-
"""
main.py - Flask 应用入口
========================
职责：创建 app、注册路由、启动服务（不写业务逻辑）

运行方式（项目根目录）：
  python -m app.main
（注意：用 -m 模块方式运行，直接 python app/main.py 会报 No module named 'app'）
"""
from pathlib import Path

from flask import Flask

from app.config import HOST, PORT, FAISS_INDEX_PATH
from app.routes import bp, store


def create_app() -> Flask:
    """应用工厂：创建并配置 Flask 实例（前端页面在 frontend/ 目录）"""
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="/static")
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        """根路径返回前端聊天页面"""
        return app.send_static_file("index.html")

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