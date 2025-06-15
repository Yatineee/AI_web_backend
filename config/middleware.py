# config/middleware.py
from fastapi.middleware.cors import CORSMiddleware

def setup_middlewares(app):
    print("✅ CORS middleware is being set up!")  # 添加这一行调试
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # ⚠️ 生产环境替换为前端域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
