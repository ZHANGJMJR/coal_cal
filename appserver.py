from waitress import serve
from app import app   # 注意：app 是你 app.py 里定义的 Flask 实例
import logging
logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    print("🚀 正在使用 Waitress 部署 Flask 服务...")
    serve(app, host="0.0.0.0", port=5001, threads=8)