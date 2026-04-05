"""
柳林桥知识图谱服务 - FastAPI接口
提供图纸检索、施工建议、草图生成等API
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from kg_service import LiuLinBridgeKG
from online_dwg_processor import OnlineDWGProcessor
import json
import io
from typing import List, Optional

# 创建FastAPI应用
app = FastAPI(
    title="柳林桥钢箱梁智能知识图谱服务",
    description="基于柳林桥真实图纸数据的AI知识图谱API，支持图纸检索、施工建议、草图生成、图纸尺寸解析（无需本地安装）",
    version="2.2.0"
)

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
kg = LiuLinBridgeKG()
dwg_processor = OnlineDWGProcessor()  # 使用在线处理器，无需本地ODA


@app.get("/")
def root():
    """根路径 - API信息"""
    return {
        "name": "柳林桥钢箱梁智能知识图谱服务",
        "version": "2.0.0",
        "description": "基于柳林桥真实图纸数据的AI知识图谱",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "图纸检索",
            "构件查询", 
            "施工建议",
            "草图生成",
            "规范查询"
        ]
    }


@app.get("/health")
def health():
    """健康检查接口"""
    stats = kg.get_statistics()
    return {
        "status": "healthy",
        "project": "柳林桥",
        "entities_count": stats["total_entities"],
        "drawings_count": stats["drawings_count"],
        "systems_count": stats["systems_count"],
        "processes_count": stats["processes_count"],
        "specs_count": stats["specs_count"]
    }


@app.get("/project/info")
def project_info():
    """获取柳林桥项目基本信息"""
    return {
        "projectId": "LLQ-2024-001",
        "projectName": "柳林桥钢箱梁建造项目",
        "bridgeType": "中承式拱桥（钢箱梁）",
        "location": "天津市",
        "designUnit": "中交第一航务工程局",
        "manufactureUnit": "一航局",
        "status": "在建",
        "totalDrawings": 72,
        "mainDrawings": 64,
        "smartBridgeDrawings": 4
    }


@app.get("/drawings/search")
def search_drawings(
    keyword: str = Query(..., description="搜索关键词（支持图号、图名、分类模糊匹配）"),
    limit: int = Query(20, description="返回数量限制")
):
    """
    搜索图纸
    
    示例：/drawings/search?keyword=拱肋&limit=10
    """
    results = kg.search_drawings(keyword)
    total = len(results)
    
    # 格式化返回
    formatted = []
    for d in results[:limit]:
        formatted.append({
            "drawingNo": d.get("sb:drawingNo"),
            "drawingName": d.get("sb:drawingName"),
            "category": d.get("sb:category"),
            "filePath": d.get("sb:filePath")
        })
    
    return {
        "keyword": keyword,
        "total": total,
        "returned": len(formatted),
        "data": formatted
    }


@app.get("/drawings/category/{category}")
def get_drawings_by_category(category: str):
    """
    按分类获取图纸
    
    分类包括：下部结构、拱肋结构、主梁系统、吊索系统、桥面系、智慧桥梁、总体、施工临时结构
    """
    results = kg.query_drawings(category=category)
    
    return {
        "category": category,
        "count": len(results),
        "data": [
            {
                "drawingNo": d.get("sb:drawingNo"),
                "drawingName": d.get("sb:drawingName"),
                "filePath": d.get("sb:filePath")
            }
            for d in results
        ]
    }


@app.get("/drawings/all-categories")
def get_all_categories():
    """获取所有图纸分类"""
    categories = kg.get_all_drawings_by_category()
    
    result = {}
    for cat, drawings in categories.items():
        result[cat] = {
            "count": len(drawings),
            "drawings": [
                {
                    "drawingNo": d.get("sb:drawingNo"),
                    "drawingName": d.get("sb:drawingName")
                }
                for d in drawings
            ]
        }
    
    return result


@app.get("/drawings/{drawing_no}")
def get_drawing_detail(drawing_no: str):
    """获取单张图纸详细信息"""
    drawing = kg.get_drawing_by_no(drawing_no)
    
    if not drawing:
        raise HTTPException(status_code=404, detail=f"图纸 {drawing_no} 不存在")
    
    return {
        "drawingNo": drawing.get("sb:drawingNo"),
        "drawingName": drawing.get("sb:drawingName"),
        "category": drawing.get("sb:category"),
        "filePath": drawing.get("sb:filePath"),
        "relatedComponents": drawing.get("sb:relatedComponents", [])
    }


@app.get("/components/systems")
def get_component_systems():
    """获取所有构件系统"""
    systems = []
    for name, entity in kg.components_index.items():
        systems.append({
            "systemName": name,
            "description": entity.get("sb:description"),
            "components": entity.get("sb:components", [])
        })
    
    return {"systems": systems}


@app.get("/components/{system_name}/construction-guide")
def get_construction_guide(system_name: str):
    """
    获取构件系统的施工指导
    
    系统名称：下部结构系统、拱肋结构系统、主梁系统、吊索系统、桥面系及附属设施、智慧桥梁系统
    """
    # 查找对应的系统ID
    system_id = None
    for sid, entity in kg.components_index.items():
        if system_name in sid or sid in system_name:
            system_id = entity.get("@id")
            break
    
    if not system_id:
        raise HTTPException(status_code=404, detail=f"构件系统 {system_name} 不存在")
    
    guide = kg.get_construction_guide(system_id)
    
    return guide


@app.get("/sketch/generate")
def generate_sketch(
    sketch_type: str = Query(..., description="草图类型：arch_installation(拱肋安装), beam_fabrication(主梁制作), deck_construction(桥面系施工)"),
    format: str = Query("svg", description="输出格式：svg、json")
):
    """
    生成施工草图
    
    根据施工类型生成简化的施工流程草图
    """
    params = kg.get_sketch_params(sketch_type)
    
    if not params:
        raise HTTPException(status_code=400, detail=f"不支持的草图类型: {sketch_type}")
    
    if format == "json":
        return params
    
    # 生成SVG格式的简单草图
    svg_content = generate_svg_sketch(params)
    
    return PlainTextResponse(
        content=svg_content,
        media_type="image/svg+xml"
    )


def generate_svg_sketch(params: dict) -> str:
    """生成SVG施工草图"""
    title = params.get("title", "施工草图")
    steps = params.get("steps", [])
    components = params.get("components", [])
    notes = params.get("notes", [])
    
    # SVG基础设置
    width = 800
    height = 600
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8f9fa"/>',
        f'<text x="400" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">{title}</text>',
        
        # 构件区域
        '<rect x="20" y="50" width="760" height="100" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>',
        '<text x="30" y="75" font-size="14" font-weight="bold" fill="#1976d2">构件：</text>',
        f'<text x="30" y="100" font-size="12" fill="#333">{", ".join(components)}</text>',
    ]
    
    # 施工步骤
    y_start = 180
    for i, step in enumerate(steps):
        y = y_start + i * 50
        
        # 步骤圆圈
        svg_parts.append(f'<circle cx="50" cy="{y}" r="15" fill="#4caf50"/>')
        svg_parts.append(f'<text x="50" y="{y+5}" text-anchor="middle" font-size="12" fill="white" font-weight="bold">{i+1}</text>')
        
        # 步骤文字
        svg_parts.append(f'<text x="80" y="{y+5}" font-size="14" fill="#333">{step}</text>')
        
        # 连接线
        if i < len(steps) - 1:
            svg_parts.append(f'<line x1="50" y1="{y+15}" x2="50" y2="{y+35}" stroke="#999" stroke-width="2" marker-end="url(#arrow)"/>')
    
    # 关键图纸和注意事项
    key_drawings = params.get("key_drawings", [])
    y_notes = y_start + len(steps) * 50 + 30
    
    svg_parts.append(f'<text x="30" y="{y_notes}" font-size="14" font-weight="bold" fill="#d32f2f">关键图纸：</text>')
    svg_parts.append(f'<text x="30" y="{y_notes+20}" font-size="12" fill="#333">{", ".join(key_drawings)}</text>')
    
    svg_parts.append(f'<text x="30" y="{y_notes+50}" font-size="14" font-weight="bold" fill="#d32f2f">注意事项：</text>')
    for i, note in enumerate(notes):
        svg_parts.append(f'<text x="30" y="{y_notes+70+i*18}" font-size="12" fill="#333">• {note}</text>')
    
    # 箭头定义
    svg_parts.append('''
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#999"/>
        </marker>
    </defs>
    ''')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


@app.get("/processes/list")
def list_processes():
    """获取所有施工工序"""
    processes = []
    for name, entity in kg.processes_index.items():
        processes.append({
            "processId": entity.get("sb:processId"),
            "processName": entity.get("sb:processName"),
            "category": entity.get("sb:category"),
            "description": entity.get("sb:description"),
            "standardHours": entity.get("sb:standardHours")
        })
    
    return {"processes": processes}


@app.get("/specs/list")
def list_specifications():
    """获取所有技术规范"""
    specs = []
    for spec_id, entity in kg.specs_index.items():
        specs.append({
            "specId": entity.get("sb:specId"),
            "specName": entity.get("sb:specName"),
            "category": entity.get("sb:category"),
            "filePath": entity.get("sb:filePath")
        })
    
    return {"specifications": specs}


@app.get("/kg/export")
def export_knowledge_graph(
    format: str = Query("jsonld", description="导出格式: jsonld 或 csv"),
    category: str = Query(None, description="按分类导出")
):
    """导出知识图谱数据"""
    try:
        data = kg.export(format=format, category=category)
        
        if format == "jsonld":
            media_type = "application/ld+json"
            filename = "liulin_bridge_kg.jsonld"
        else:
            media_type = "text/csv"
            filename = "liulin_bridge_kg.csv"
        
        return PlainTextResponse(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.get("/drawings/{drawing_no}/parse")
def parse_drawing_content(drawing_no: str):
    """
    解析图纸内容（尝试提取尺寸、实体、图层信息）
    
    ⚠️ 注意：此功能需要图纸为DXF格式，或配合DWG转DXF工具使用
    
    示例：/drawings/S2-1-2-5/parse
    """
    # 获取图纸信息
    drawing = kg.get_drawing_by_no(drawing_no)
    if not drawing:
        raise HTTPException(status_code=404, detail=f"图纸 {drawing_no} 不存在")
    
    file_path = drawing.get("sb:filePath", "")
    
    # 尝试解析（如果安装了ezdxf且文件可解析）
    try:
        from drawing_parser import DrawingParser
        parser = DrawingParser()
        
        # 尝试解析
        result = parser.parse_dwg(file_path)
        
        return {
            "drawingNo": drawing_no,
            "drawingName": drawing.get("sb:drawingName"),
            "filePath": file_path,
            "parseStatus": "success" if "error" not in result else "partial",
            "content": result,
            "note": "如需完整解析，请将DWG转换为DXF格式，或安装ODA File Converter"
        }
    
    except ImportError:
        # ezdxf 未安装
        return {
            "drawingNo": drawing_no,
            "drawingName": drawing.get("sb:drawingName"),
            "filePath": file_path,
            "parseStatus": "metadata_only",
            "content": {
                "layers": [],
                "entities": {"lines": 0, "circles": 0, "arcs": 0, "dimensions": 0},
                "note": "CAD解析库未安装"
            },
            "setupGuide": {
                "step1": "pip install ezdxf",
                "step2": "对于DWG文件，需要先用 ODA File Converter 转换为DXF",
                "odaConverter": "https://www.opendesign.com/guestfiles/oda_file_converter",
                "alternative": "或使用在线转换工具将DWG转DXF"
            }
        }
    
    except Exception as e:
        return {
            "drawingNo": drawing_no,
            "parseStatus": "error",
            "error": str(e),
            "note": "图纸解析需要DXF格式或专用转换工具"
        }


@app.get("/drawings/{drawing_no}/dimensions")
def get_drawing_dimensions(drawing_no: str):
    """
    获取图纸尺寸信息（Web端直接使用，无需本地安装）
    
    工作原理：
    1. 优先查找预转换的DXF文件 → 直接解析返回尺寸
    2. 只有DWG → 返回元数据 + 在线转换建议
    
    示例：/drawings/S2-1-2-5/dimensions
    """
    # 获取图纸信息
    drawing = kg.get_drawing_by_no(drawing_no)
    if not drawing:
        raise HTTPException(status_code=404, detail=f"图纸 {drawing_no} 不存在")
    
    drawing_name = drawing.get("sb:drawingName")
    file_path = drawing.get("sb:filePath", "")
    
    # 使用在线处理器获取图纸（带降级策略）
    result = dwg_processor.get_drawing_with_fallback(drawing_no, drawing_name, file_path)
    
    # 简化输出
    response = {
        "drawingNo": drawing_no,
        "drawingName": drawing_name,
        "status": result["status"],
        "filePath": file_path
    }
    
    if result["status"] == "parsed" and result["dimensions"]:
        # 成功解析DXF
        dims = result["dimensions"]
        response["dimensions"] = {
            "summary": dims.get("summary", {}),
            "mainDimensions": dims.get("summary", {}).get("mainDimensions", []),
            "entityCount": dims.get("entities", {}),
            "boundingBox": dims.get("boundingBox"),
            "layersCount": len(dims.get("layers", []))
        }
        response["note"] = "✅ 尺寸数据已从DXF文件提取"
    
    elif result["status"] == "dwg_only":
        # 只有DWG，需要转换
        response["solution"] = result["solution"]
        response["note"] = "⚠️ 需要DXF格式才能解析尺寸"
    
    elif result["status"] == "not_found":
        response["error"] = "未找到图纸文件"
        response["searchPath"] = str(dwg_processor.dwg_base)
    
    return response


@app.get("/system/dxf-status")
def check_dxf_status():
    """
    检查DXF图纸状态
    
    返回有多少图纸已转换为DXF格式
    """
    # 获取所有图纸
    all_drawings = []
    for entity in kg.graph:
        if 'Drawing' in entity.get('@type', ''):
            all_drawings.append({
                "drawingNo": entity.get('sb:drawingNo'),
                "drawingName": entity.get('sb:drawingName'),
                "filePath": entity.get('sb:filePath')
            })
    
    # 批量检查
    check_result = dwg_processor.batch_check_drawings(all_drawings[:20])  # 检查前20张
    
    return {
        "totalDrawings": len(all_drawings),
        "checked": check_result["total"],
        "withDXF": check_result["withDXF"],
        "withDWGOnly": check_result["withDWGOnly"],
        "missing": check_result["missing"],
        "details": check_result["details"],
        "dxfPath": str(dwg_processor.dxf_base),
        "setupGuide": {
            "title": "如何获得DXF文件（三种方案）",
            "options": [
                {
                    "name": "方案1：预转换（推荐）",
                    "description": "将DWG批量转换为DXF，上传到GitHub",
                    "pros": ["一次转换永久使用", "Web端直接解析", "速度最快"],
                    "command": "odafileconverter './柳林桥CAD图纸' './柳林桥DXF图纸' ACAD2018 DXF 0 1"
                },
                {
                    "name": "方案2：在线转换",
                    "description": "使用AnyConv等在线服务，单个转换",
                    "url": "https://anyconv.com/dwg-to-dxf-converter",
                    "pros": ["无需安装软件", "即用即转"],
                    "cons": ["需要手动上传下载", "不适合批量"]
                },
                {
                    "name": "方案3：CAD软件",
                    "description": "用AutoCAD/ZWCAD打开DWG，另存为DXF",
                    "command": "文件 → 另存为 → 格式选DXF",
                    "pros": ["最可靠", "控制选项多"],
                    "cons": ["需要CAD软件", "手动操作"]
                }
            ]
        }
    }


@app.post("/drawings/batch-convert-guide")
def batch_convert_guide():
    """
    批量转换指导
    
    提供完整的DWG→DXF批量转换方案
    """
    return {
        "title": "柳林桥图纸批量转换方案",
        "steps": [
            {
                "step": 1,
                "title": "安装ODA File Converter",
                "windows": "下载安装包运行即可",
                "linux": "下载deb包: dpkg -i odafileconverter.deb",
                "docker": "docker pull opendesign/odafileconverter"
            },
            {
                "step": 2,
                "title": "执行批量转换",
                "command": f"odafileconverter '{dwg_processor.dwg_base}' '{dwg_processor.dxf_base}' ACAD2018 DXF 0 1",
                "note": "转换72张图纸约需5-10分钟"
            },
            {
                "step": 3,
                "title": "验证转换结果",
                "check": f"ls -la {dwg_processor.dxf_base}",
                "expected": "72个DXF文件"
            },
            {
                "step": 4,
                "title": "上传到GitHub",
                "commands": [
                    "cd /root/.openclaw/workspace/一航局课题交付包/cad-drawings",
                    "git add 柳林桥DXF图纸/",
                    "git commit -m 'Add DXF files for online parsing'",
                    "git push"
                ]
            }
        ],
        "alternative": "如果不想安装软件，可以联系管理员预转换好后统一上传"
    }


@app.get("/ai/query")
def ai_query_with_dimensions(
    question: str = Query(..., description="自然语言问题，如：Z1节段的尺寸是多少？")
):
    """
    AI问答接口（增强版，支持尺寸查询）
    
    根据问题自动解析并返回图纸尺寸信息
    """
    question_lower = question.lower()
    response = {
        "question": question,
        "answer": "",
        "dimensions": None,
        "relatedDrawings": [],
        "relatedProcesses": [],
        "suggestions": []
    }
    
    # 梁段尺寸查询
    beam_patterns = [
        (r'z1', 'Z1'), (r'z2', 'Z2'), (r'z3', 'Z3'), (r'z4', 'Z4'), (r'z5', 'Z5'),
        (r'z6', 'Z6'), (r'z7', 'Z7'), (r'z8', 'Z8'), (r'z9', 'Z9'), (r'z10', 'Z10'),
        (r'c1', 'C1'), (r'c2', 'C2'), (r'c3', 'C3'), (r'c4', 'C4'), (r'c5', 'C5'),
    ]
    
    import re
    for pattern, segment in beam_patterns:
        if re.search(pattern, question_lower):
            # 尝试获取尺寸
            try:
                dim_result = dwg_processor.get_beam_dimensions(segment)
                
                if "parseResult" in dim_result:
                    parse_data = dim_result["parseResult"]
                    dims = parse_data.get("dimensions", {})
                    
                    # 构建回答
                    linear_dims = dims.get("linear", [])
                    circles = dims.get("radii", [])
                    
                    response["answer"] = f"**{segment}节段尺寸信息**\n\n"
                    response["answer"] += f"图纸：{dim_result.get('dxfPath', '未解析')}\n\n"
                    
                    if linear_dims:
                        # 提取前5个尺寸
                        sizes = [str(d.get("value", "未知")) for d in linear_dims[:5]]
                        response["answer"] += f"主要尺寸：{', '.join(sizes)} mm\n"
                    
                    if circles:
                        response["answer"] += f"\n圆孔数量：{len(circles)} 个\n"
                        # 显示前3个圆的直径
                        diameters = [str(round(c.get("diameter", 0), 1)) for c in circles[:3]]
                        response["answer"] += f"孔径示例：{', '.join(diameters)} mm\n"
                    
                    response["answer"] += f"\n实体统计：线{parse_data.get('entityCount', {}).get('lines', 0)}条, "
                    response["answer"] += f"圆{circles and len(circles) or 0}个, "
                    response["answer"] += f"尺寸标注{len(linear_dims)}个"
                    
                    response["dimensions"] = {
                        "segment": segment,
                        "linearDimensions": len(linear_dims),
                        "circles": len(circles),
                        "boundingBox": parse_data.get("boundingBox")
                    }
                    
                    # 找到对应图纸
                    drawing_map = {
                        "Z1": "S2-1-2-5", "Z2": "S2-1-2-6", "Z3": "S2-1-2-7",
                        "C1": "S2-1-2-15", "主梁": "S2-1-3-5"
                    }
                    if segment in drawing_map:
                        drawing = kg.get_drawing_by_no(drawing_map[segment])
                        if drawing:
                            response["relatedDrawings"].append({
                                "drawingNo": drawing_map[segment],
                                "drawingName": drawing.get("sb:drawingName")
                            })
                    
                    response["suggestions"] = [
                        f"查看完整尺寸：GET /beams/{segment}/dimensions",
                        "如需精确尺寸，请用AutoCAD打开原始DWG文件核对"
                    ]
                    
                else:
                    response["answer"] = f"{segment}节段的图纸信息已找到，但尺寸数据需要转换后解析。"
                    response["suggestions"] = [
                        "安装ODA File Converter后重试",
                        f"调用 /beams/{segment}/dimensions 获取详细尺寸"
                    ]
                
            except Exception as e:
                response["answer"] = f"查询{segment}节段时出错：{str(e)}"
            
            return response
    
    # 其他查询（保留原有逻辑）
    if "拱肋" in question_lower or "拱" in question_lower:
        response["answer"] = "柳林桥主桥为中承式拱桥，拱肋系统包括主拱Z1-Z10（10节段）、次拱C1-C5（5节段）及横撑HC1-HC2。"
        response["relatedDrawings"] = kg.query_drawings(category="拱肋结构")[:5]
        response["suggestions"] = [
            "查询具体节段尺寸：Z1节段的尺寸是多少？",
            "查看图纸 S2-1-2-2、3 了解拱肋节段划分"
        ]
    
    elif "主梁" in question_lower or "梁段" in question_lower:
        response["answer"] = "柳林桥主梁系统包括主梁节段和拱梁结合段，采用钢箱梁结构。可查询具体节段的详细尺寸。"
        response["relatedDrawings"] = kg.query_drawings(category="主梁系统")[:5]
        response["suggestions"] = [
            "查询主梁尺寸：主梁的尺寸是多少？",
            "查看 S2-1-3-2 了解梁段划分"
        ]
    
    else:
        response["answer"] = "我可以帮您查询柳林桥的图纸、构件尺寸、施工建议等。\n\n**试试这样问：**\n- Z1节段的尺寸是多少？\n- 主梁的详细尺寸？\n- C1拱肋有哪些尺寸标注？"
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
