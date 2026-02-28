"""
配置管理
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8081"))
API_WORKERS = int(os.getenv("API_WORKERS", "1"))

# 大模型配置
LLM_TYPE = os.getenv("LLM_TYPE", "openai")  # openai / azure / local
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# 本地模型配置（vLLM等）
LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:8000/v1")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "Qwen2.5-32B-Instruct")

# 知识图谱服务配置（交付物1）
KG_SERVICE_URL = os.getenv("KG_SERVICE_URL", "http://localhost:8000")
KG_EXPORT_ENDPOINT = f"{KG_SERVICE_URL}/kg/export"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chat.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 会话配置
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 秒
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
