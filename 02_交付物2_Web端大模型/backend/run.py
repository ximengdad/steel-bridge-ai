#!/usr/bin/env python3
"""
启动脚本
"""
import uvicorn
from app.config import API_HOST, API_PORT


if __name__ == "__main__":
    print(f"🚀 启动钢箱梁智能助手服务")
    print(f"  地址: http://{API_HOST}:{API_PORT}")
    print(f"  文档: http://{API_HOST}:{API_PORT}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
