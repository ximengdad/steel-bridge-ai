"""
在线图纸处理方案 - 无需本地安装ODA
提供三种方式获取DXF文件进行解析
"""
import os
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import base64
import tempfile


class OnlineDWGProcessor:
    """
    在线DWG处理 - 无需本地ODA转换器
    
    方案优先级：
    1. 使用预转换的DXF文件（推荐，已转换好）
    2. 调用在线转换API（AnyConv/CloudConvert）
    3. 返回图纸元数据+手动下载链接
    """
    
    def __init__(self, 
                 dwg_base_path: str = None,
                 dxf_base_path: str = None):
        """
        初始化
        
        Args:
            dwg_base_path: DWG图纸路径
            dxf_base_path: DXF图纸路径（预转换好的）
        """
        base = "/root/.openclaw/workspace/一航局课题交付包/cad-drawings"
        
        self.dwg_base = Path(dwg_base_path) if dwg_base_path else Path(base) / "柳林桥CAD图纸"
        self.dxf_base = Path(dxf_base_path) if dxf_base_path else Path(base) / "柳林桥DXF图纸"
        
        # 确保目录存在
        self.dxf_base.mkdir(parents=True, exist_ok=True)
    
    def get_dxf_path(self, drawing_no: str, drawing_name: str = None) -> Optional[Path]:
        """
        获取DXF文件路径
        
        查找顺序：
        1. 预转换的DXF目录
        2. 与DWG同目录（可能已转换）
        """
        # 尝试多种命名方式
        possible_names = [
            f"{drawing_no}.dxf",
            f"{drawing_no} {drawing_name}.dxf" if drawing_name else None,
            f"*{drawing_no}*.dxf",
        ]
        
        # 在DXF目录查找
        if self.dxf_base.exists():
            for name in possible_names:
                if not name:
                    continue
                if '*' in name:
                    matches = list(self.dxf_base.rglob(name))
                    if matches:
                        return matches[0]
                else:
                    path = self.dxf_base / name
                    if path.exists():
                        return path
        
        # 在DWG目录查找（可能同目录有DXF）
        for name in possible_names:
            if not name:
                continue
            if '*' in name:
                matches = list(self.dwg_base.rglob(name))
                if matches:
                    return matches[0]
            else:
                path = self.dwg_base.rglob(name)
                for p in path:
                    return p
        
        return None
    
    def parse_dxf_online(self, file_path: str) -> Dict[str, Any]:
        """
        解析DXF文件内容
        
        纯Python实现，无需外部工具
        """
        try:
            import ezdxf
        except ImportError:
            return {
                "error": "ezdxf库未安装",
                "solution": "pip install ezdxf",
                "note": "这是唯一需要的依赖，纯Python，无需系统级安装"
            }
        
        try:
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # 提取关键信息
            result = {
                "fileName": Path(file_path).name,
                "layers": [],
                "entities": {
                    "lines": 0, "circles": 0, "arcs": 0,
                    "polylines": 0, "dimensions": 0, "texts": 0
                },
                "extractedDimensions": [],
                "boundingBox": None
            }
            
            # 图层
            for layer in doc.layers:
                result["layers"].append({
                    "name": layer.dxf.name,
                    "color": layer.dxf.color
                })
            
            # 实体统计和关键尺寸提取
            for entity in msp:
                etype = entity.dxftype()
                
                if etype == "LINE":
                    result["entities"]["lines"] += 1
                
                elif etype == "CIRCLE":
                    result["entities"]["circles"] += 1
                    # 提取圆信息（可能是螺栓孔）
                    result["extractedDimensions"].append({
                        "type": "circle",
                        "description": f"圆孔直径 {entity.dxf.radius * 2:.1f}mm",
                        "radius": entity.dxf.radius,
                        "diameter": entity.dxf.radius * 2,
                        "center": [round(entity.dxf.center.x, 2), round(entity.dxf.center.y, 2)]
                    })
                
                elif etype == "ARC":
                    result["entities"]["arcs"] += 1
                
                elif etype in ["LWPOLYLINE", "POLYLINE"]:
                    result["entities"]["polylines"] += 1
                
                elif etype == "DIMENSION":
                    result["entities"]["dimensions"] += 1
                    # 提取尺寸标注
                    try:
                        text = entity.dxf.text or ""
                        actual = getattr(entity.dxf, 'actual_measurement', None)
                        
                        # 解析尺寸值
                        import re
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match or actual:
                            result["extractedDimensions"].append({
                                "type": "linear" if not text.startswith(('R', '%%c', 'Φ')) else 
                                       "radius" if text.startswith('R') else "diameter",
                                "text": text,
                                "value": actual or float(match.group(1)) if match else None,
                                "description": f"尺寸标注: {text}"
                            })
                    except:
                        pass
                
                elif etype in ["TEXT", "MTEXT"]:
                    result["entities"]["texts"] += 1
                    # 提取可能的尺寸文字
                    try:
                        text = entity.dxf.text if hasattr(entity.dxf, 'text') else str(entity.text)
                        # 匹配常见的尺寸格式
                        import re
                        if re.search(r'\d+\.?\d*\s*(mm|cm|m)?', text):
                            result["extractedDimensions"].append({
                                "type": "text",
                                "text": text[:50],
                                "description": f"文字标注: {text[:50]}"
                            })
                    except:
                        pass
            
            # 包围盒
            try:
                ext = msp.extents()
                result["boundingBox"] = {
                    "min": [round(ext.extmin.x, 2), round(ext.extmin.y, 2)],
                    "max": [round(ext.extmax.x, 2), round(ext.extmax.y, 2)],
                    "width": round(ext.extmax.x - ext.extmin.x, 2),
                    "height": round(ext.extmax.y - ext.extmin.y, 2)
                }
            except:
                pass
            
            # 统计摘要
            result["summary"] = {
                "totalEntities": sum(result["entities"].values()),
                "totalDimensionsExtracted": len(result["extractedDimensions"]),
                "mainDimensions": result["extractedDimensions"][:10]  # 前10个尺寸
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"解析失败: {str(e)}",
                "filePath": file_path
            }
    
    def get_drawing_with_fallback(self, drawing_no: str, drawing_name: str = None, file_path: str = None) -> Dict[str, Any]:
        """
        获取图纸信息（带降级策略）
        
        优先级：
        1. 有DXF文件 → 解析尺寸
        2. 只有DWG → 返回元数据 + 转换建议
        """
        result = {
            "drawingNo": drawing_no,
            "drawingName": drawing_name,
            "status": "checking",
            "hasDXF": False,
            "hasDWG": False,
            "dimensions": None,
            "solution": None
        }
        
        # 1. 查找DXF
        dxf_path = self.get_dxf_path(drawing_no, drawing_name)
        
        if dxf_path and dxf_path.exists():
            result["hasDXF"] = True
            result["dxfPath"] = str(dxf_path)
            result["status"] = "parsed"
            result["dimensions"] = self.parse_dxf_online(str(dxf_path))
            return result
        
        # 2. 查找DWG
        if file_path:
            dwg_path = self.dwg_base.parent / file_path
            if dwg_path.exists():
                result["hasDWG"] = True
                result["dwgPath"] = str(dwg_path)
                result["status"] = "dwg_only"
                result["solution"] = {
                    "message": "找到DWG文件，但缺少DXF格式",
                    "options": [
                        {
                            "method": "在线转换",
                            "description": "使用AnyConv等在线服务转换",
                            "url": f"https://anyconv.com/dwg-to-dxf-converter"
                        },
                        {
                            "method": "预转换",
                            "description": "将所有DWG预转换为DXF后重新上传",
                            "note": "推荐方案，转换一次永久使用"
                        },
                        {
                            "method": "CAD软件",
                            "description": "用AutoCAD打开后另存为DXF格式",
                            "command": "SAVEAS → DXF格式"
                        }
                    ],
                    "downloadUrl": f"https://github.com/ximengdad/CAD/blob/main/{file_path}"
                }
                return result
        
        # 3. 都没找到
        result["status"] = "not_found"
        result["solution"] = {
            "message": "未找到图纸文件",
            "searchPath": str(self.dwg_base)
        }
        
        return result
    
    def batch_check_drawings(self, drawings_list: list) -> Dict[str, Any]:
        """
        批量检查图纸状态
        
        Args:
            drawings_list: 图纸列表，每个元素包含 drawingNo, drawingName, filePath
        """
        results = {
            "total": len(drawings_list),
            "withDXF": 0,
            "withDWGOnly": 0,
            "missing": 0,
            "details": []
        }
        
        for drawing in drawings_list:
            check = self.get_drawing_with_fallback(
                drawing.get("drawingNo"),
                drawing.get("drawingName"),
                drawing.get("filePath")
            )
            
            results["details"].append({
                "drawingNo": drawing.get("drawingNo"),
                "status": check["status"],
                "hasDXF": check["hasDXF"],
                "hasDWG": check["hasDWG"]
            })
            
            if check["hasDXF"]:
                results["withDXF"] += 1
            elif check["hasDWG"]:
                results["withDWGOnly"] += 1
            else:
                results["missing"] += 1
        
        return results


# 快速测试
if __name__ == "__main__":
    processor = OnlineDWGProcessor()
    
    print("=== 在线图纸处理测试 ===")
    print(f"DWG目录: {processor.dwg_base}")
    print(f"DXF目录: {processor.dxf_base}")
    print()
    
    # 检查是否有DXF文件
    if processor.dxf_base.exists():
        dxf_files = list(processor.dxf_base.rglob("*.dxf"))
        print(f"找到 {len(dxf_files)} 个DXF文件")
        
        if dxf_files:
            print("\n示例解析（第一个DXF文件）:")
            result = processor.parse_dxf_online(str(dxf_files[0]))
            print(f"  文件: {result.get('fileName')}")
            print(f"  实体: {result.get('summary', {}).get('totalEntities', 0)}")
            print(f"  尺寸: {result.get('summary', {}).get('totalDimensionsExtracted', 0)}")
    else:
        print("未找到DXF目录")
        print("\n如需完整解析，请先将DWG转换为DXF格式:")
        print("  方法1: 使用ODA File Converter批量转换")
        print("  方法2: 上传到 https://anyconv.com/dwg-to-dxf-converter")
