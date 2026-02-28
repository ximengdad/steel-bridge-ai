"""
主入口 - FastAPI应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import API_HOST, API_PORT, LOG_LEVEL
from app.models.schemas import (
    ChatRequest, ChatResponse, SessionCreate, SessionInfo,
    SceneType, ExportRequest
)
from app.agents import get_agent
from app.services.kg_client import kg_client


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    print("🚀 钢箱梁智能助手服务启动")
    print(f"  知识图谱服务: {kg_client.base_url}")
    yield
    print("👋 服务关闭")


# 创建应用
app = FastAPI(
    title="钢箱梁智能助手",
    description="基于大语言模型的钢箱梁工程建议生成系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟会话存储（生产环境应使用Redis/DB）
sessions = {}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "钢箱梁智能助手",
        "version": "1.0.0",
        "docs": "/docs",
        "scenes": ["design", "production", "quality", "assembly"]
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "钢箱梁智能助手"}


@app.post("/api/v2/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口（核心功能）
    
    流程：
    1. 确定场景
    2. 从交付物1导出知识图谱
    3. Agent处理生成建议
    4. 返回带证据的回答
    """
    try:
        # 1. 获取或创建会话
        session_id = request.session_id or f"session_{len(sessions)}"
        
        # 2. 获取对应场景的Agent
        agent = get_agent(request.scene)
        
        # 3. 从交付物1导出知识图谱（关键！）
        project_id = request.context.get("project_id")
        kg_data = await kg_client.export_kg(project_id=project_id)
        
        # 4. Agent处理
        result = await agent.process(
            message=request.message,
            context=request.context,
            kg_data=kg_data
        )
        
        # 5. 构建响应
        return ChatResponse(
            message_id=f"msg_{session_id}_{len(sessions)}",
            content=result["content"],
            scene=request.scene,
            evidence=result.get("evidence", []),
            suggestions=[{"type": "follow_up", "content": "查看详细分析"}]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/sessions")
async def create_session(request: SessionCreate):
    """创建会话"""
    session_id = f"ses_{len(sessions)}"
    sessions[session_id] = {
        "session_id": session_id,
        "scene": request.scene,
        "project_id": request.project_id,
        "title": request.title or f"新会话-{session_id}",
        "messages": []
    }
    
    return SessionInfo(
        session_id=session_id,
        scene=request.scene,
        project_id=request.project_id,
        title=request.title,
        created_at=__import__('datetime').datetime.now(),
        updated_at=__import__('datetime').datetime.now()
    )


@app.get("/api/v2/templates")
async def get_templates(scene: SceneType = None):
    """获取提问模板"""
    templates = {
        SceneType.DESIGN: [
            {"id": "d1", "content": "【构件B-001】的设计参数是否合理？"},
            {"id": "d2", "content": "类似【主跨680m斜拉桥】的案例有哪些？"},
            {"id": "d3", "content": "【顶板厚度24mm】是否符合规范？"}
        ],
        SceneType.PRODUCTION: [
            {"id": "p1", "content": "项目【PRJ-001】的生产进度如何？"},
            {"id": "p2", "content": "【焊接工序】是否存在瓶颈？"},
            {"id": "p3", "content": "【下周】的产能能否满足交付？"}
        ],
        SceneType.QUALITY: [
            {"id": "q1", "content": "【焊缝气孔】可能是什么原因？"},
            {"id": "q2", "content": "【B-001构件】的质检记录如何？"},
            {"id": "q3", "content": "【A类缺陷】的处理流程是什么？"}
        ],
        SceneType.ASSEMBLY: [
            {"id": "a1", "content": "【S01节段】的装配步骤是什么？"},
            {"id": "a2", "content": "【顶板吊装】的路径如何规划？"},
            {"id": "a3", "content": "【现场空间受限】如何解决？"}
        ]
    }
    
    if scene:
        return {"scene": scene, "templates": templates.get(scene, [])}
    return templates


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)

# 添加前端静态文件服务
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 挂载前端静态文件
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    """服务前端页面"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "钢箱梁智能助手 API 服务运行中"}
