"""
知识图谱客户端 - 调用交付物1的导出接口
"""
import httpx
import json
from typing import Dict, Optional
from app.config import KG_EXPORT_ENDPOINT


class KGClient:
    """知识图谱服务客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or KG_EXPORT_ENDPOINT.replace("/kg/export", "")
        self.export_url = f"{self.base_url}/kg/export"
        self.query_url = f"{self.base_url}/kg/query"
    
    async def export_kg(self, project_id: str = None, format: str = "jsonld") -> Dict:
        """
        从交付物1导出知识图谱
        
        Args:
            project_id: 项目ID，None则导出全部
            format: 导出格式
        
        Returns:
            知识图谱数据（JSON格式）
        """
        params = {"format": format}
        if project_id:
            params["project_id"] = project_id
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.export_url,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                
                if format == "jsonld":
                    return response.json()
                else:
                    return {"raw_data": response.text}
            
            except httpx.HTTPError as e:
                print(f"知识图谱导出失败: {e}")
                # 返回空数据，不阻断主流程
                return {"@graph": []}
    
    async def query_entities(self, entity_type: str = None, project_id: str = None) -> Dict:
        """查询实体"""
        params = {}
        if entity_type:
            params["type"] = entity_type
        if project_id:
            params["project_id"] = project_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.query_url, params=params)
            return response.json()
    
    def format_for_llm(self, kg_data: Dict) -> str:
        """
        将知识图谱格式化为大模型可读的文本
        
        Args:
            kg_data: JSON-LD格式的知识图谱数据
        
        Returns:
            自然语言描述文本
        """
        if not kg_data or "@graph" not in kg_data:
            return "暂无知识图谱数据。"
        
        entities = kg_data["@graph"]
        sections = []
        
        # 按类型分组
        from collections import defaultdict
        by_type = defaultdict(list)
        
        for entity in entities:
            etype = entity.get("@type", "Unknown").replace("sb:", "")
            by_type[etype].append(entity)
        
        # 生成描述
        for etype, items in by_type.items():
            if etype == "Project" and items:
                p = items[0]
                sections.append(
                    f"项目：{p.get('sb:projectName', '')}（{p.get('sb:projectId', '')}），"
                    f"类型：{p.get('sb:bridgeType', '')}。"
                )
            
            elif etype == "Beam":
                sections.append(f"包含{len(items)}个构件：")
                for b in items[:5]:  # 最多显示5个
                    sections.append(
                        f"  - 构件{b.get('sb:beamId', '')}："
                        f"{b.get('sb:beamType', '')}，"
                        f"材质{b.get('sb:materialGrade', '')}，"
                        f"厚度{b.get('sb:thickness', '')}mm"
                    )
                if len(items) > 5:
                    sections.append(f"  ... 还有{len(items)-5}个构件")
            
            elif etype == "Process":
                sections.append(f"包含{len(items)}道工序。")
            
            elif etype == "QualityIssue":
                sections.append(f"质量问题：{len(items)}个。")
                for q in items:
                    sections.append(
                        f"  - {q.get('sb:defectType', '')}（{q.get('sb:severity', '')}）："
                        f"{q.get('sb:cause', '')}"
                    )
        
        return "\n".join(sections)


# 全局客户端实例
kg_client = KGClient()
