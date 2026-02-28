"""
FastAPI接口服务 - 钢箱梁知识图谱
提供HTTP API接口，支持Web端访问
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from kg_service import SteelBridgeKG
import json

# 创建FastAPI应用
app = FastAPI(
    title="钢箱梁知识图谱服务",
    description="基于JSON-LD的钢箱梁全生命周期知识图谱API",
    version="1.0.0"
)

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化知识图谱服务
# 注意：实际使用时确保data/kg_steel_bridge.jsonld存在
try:
    kg = SteelBridgeKG("data/kg_steel_bridge.jsonld")
    print(f"✅ 知识图谱加载成功: {len(kg.graph)} 个实体")
except FileNotFoundError:
    print("⚠️ 警告: 数据文件不存在，请先运行 init_data.py 创建示例数据")
    kg = None


@app.get("/")
def root():
    """根路径 - API信息"""
    return {
        "name": "钢箱梁知识图谱服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    """
    健康检查接口
    
    Returns:
        服务状态和数据量统计
    """
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    stats = kg.get_statistics()
    return {
        "status": "healthy",
        "entities_count": stats["total_entities"],
        "entity_types": stats["entity_types"],
        "projects": stats["projects"]
    }


@app.get("/kg/entity/{entity_id}")
def get_entity(entity_id: str):
    """
    根据ID获取实体详情
    
    Args:
        entity_id: 实体ID（如Project_PRJ_001, Beam_B_001等）
    
    Returns:
        实体详细信息
    """
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    entity = kg.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"实体 {entity_id} 不存在")
    
    return entity


@app.get("/kg/query")
def query_entities(
    type: str = Query(None, description="实体类型（如Project, Beam, Process, QualityIssue）"),
    project_id: str = Query(None, description="项目ID过滤"),
    limit: int = Query(100, description="返回数量限制")
):
    """
    查询实体列表
    
    Args:
        type: 实体类型
        project_id: 项目ID
        limit: 数量限制
    
    Returns:
        实体列表
    """
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    results = kg.query(type, projectId=project_id) if type else kg.graph
    total = len(results)
    
    return {
        "total": total,
        "returned": min(limit, total),
        "data": results[:limit]
    }


@app.get("/kg/project/{project_id}/beams")
def get_project_beams(project_id: str):
    """获取项目的所有构件"""
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    beams = kg.get_project_beams(project_id)
    return {
        "project_id": project_id,
        "beam_count": len(beams),
        "beams": beams
    }


@app.get("/kg/beam/{beam_id}/processes")
def get_beam_processes(beam_id: str):
    """获取构件的所有工序"""
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    processes = kg.get_beam_processes(beam_id)
    return {
        "beam_id": beam_id,
        "process_count": len(processes),
        "processes": processes
    }


@app.get("/kg/export")
def export_knowledge_graph(
    format: str = Query("jsonld", description="导出格式: jsonld 或 csv"),
    project_id: str = Query(None, description="项目ID（只导出指定项目）")
):
    """
    导出知识图谱（核心接口！满足课题要求）
    
    导出知识图谱数据，可供大模型导入使用
    
    Args:
        format: 导出格式（jsonld/csv）
        project_id: 可选，只导出指定项目的数据
    
    Returns:
        JSON-LD或CSV格式的知识图谱数据
    """
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    try:
        data = kg.export(format=format, project_id=project_id)
        
        # 根据格式设置Content-Type
        if format == "jsonld":
            media_type = "application/ld+json"
            filename = f"kg_export_{project_id or 'all'}.jsonld"
        else:
            media_type = "text/csv"
            filename = f"kg_export_{project_id or 'all'}.csv"
        
        return PlainTextResponse(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.get("/kg/statistics")
def get_statistics():
    """获取知识图谱统计信息"""
    if kg is None:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    return kg.get_statistics()


if __name__ == "__main__":
    import uvicorn
    # 启动服务
    # 访问 http://localhost:8000/docs 查看API文档
    uvicorn.run(app, host="0.0.0.0", port=8000)
