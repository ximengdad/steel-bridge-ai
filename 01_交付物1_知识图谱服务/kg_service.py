"""
钢箱梁知识图谱服务 - 简化版（JSON文件存储）
无需Neo4j，直接使用JSON-LD文件
"""
import json
from typing import List, Dict, Optional, Any


class SteelBridgeKG:
    """
    钢箱梁知识图谱服务类
    基于JSON-LD文件存储，支持查询和导出
    """
    
    def __init__(self, jsonld_file: str):
        """
        初始化知识图谱服务
        
        Args:
            jsonld_file: JSON-LD格式数据文件路径
        """
        with open(jsonld_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.context = data.get('@context', {})
        self.graph = data.get('@graph', [])
        
        # 建立索引加速查询
        self.entities = {}  # ID索引
        self.type_index = {}  # 类型索引
        self.project_index = {}  # 项目索引
        
        for item in self.graph:
            entity_id = item.get('@id', '')
            entity_type = item.get('@type', '').replace('sb:', '')
            project_id = item.get('sb:projectId', '')
            
            # ID索引
            self.entities[entity_id] = item
            
            # 类型索引
            if entity_type not in self.type_index:
                self.type_index[entity_type] = []
            self.type_index[entity_type].append(item)
            
            # 项目索引
            if project_id:
                if project_id not in self.project_index:
                    self.project_index[project_id] = []
                self.project_index[project_id].append(item)
    
    def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取实体
        
        Args:
            entity_id: 实体ID（可带或不带sb:前缀）
        
        Returns:
            实体数据字典，不存在返回None
        """
        full_id = entity_id if entity_id.startswith('sb:') else f"sb:{entity_id}"
        return self.entities.get(full_id)
    
    def get_by_type(self, entity_type: str, project_id: str = None) -> List[Dict[str, Any]]:
        """
        根据类型获取实体列表
        
        Args:
            entity_type: 实体类型（如Project, Beam, Process等）
            project_id: 可选，指定项目ID过滤
        
        Returns:
            实体列表
        """
        etype = entity_type.replace('sb:', '')
        results = self.type_index.get(etype, [])
        
        if project_id:
            results = [e for e in results if e.get('sb:projectId') == project_id]
        
        return results
    
    def query(self, entity_type: str = None, **filters) -> List[Dict[str, Any]]:
        """
        通用查询方法
        
        Args:
            entity_type: 实体类型
            **filters: 属性过滤条件（如projectId="xxx", status="已完成"）
        
        Returns:
            符合条件的实体列表
        """
        # 从类型索引开始
        if entity_type:
            etype = f"sb:{entity_type.replace('sb:', '')}"
            results = [e for e in self.graph if e.get('@type') == etype]
        else:
            results = self.graph.copy()
        
        # 应用过滤条件
        for key, value in filters.items():
            prop = f"sb:{key}"
            results = [e for e in results if e.get(prop) == value]
        
        return results
    
    def get_project_beams(self, project_id: str) -> List[Dict[str, Any]]:
        """获取指定项目的所有构件"""
        return self.query('Beam', projectId=project_id)
    
    def get_beam_processes(self, beam_id: str) -> List[Dict[str, Any]]:
        """获取指定构件的所有工序"""
        return self.query('Process', beamId=beam_id)
    
    def get_quality_issues(self, process_id: str = None) -> List[Dict[str, Any]]:
        """获取质量问题，可指定工序ID"""
        if process_id:
            return self.query('QualityIssue', processId=process_id)
        return self.get_by_type('QualityIssue')
    
    def export(self, format: str = "jsonld", project_id: str = None) -> str:
        """
        导出知识图谱（核心功能！满足课题要求）
        
        Args:
            format: 导出格式，支持jsonld/csv
            project_id: 可选，只导出指定项目的数据
        
        Returns:
            导出内容的字符串
        """
        # 筛选数据
        if project_id:
            entities = self.project_index.get(project_id, [])
            # 包含项目实体本身
            project_entity = self.get_by_id(f"Project_{project_id}")
            if project_entity and project_entity not in entities:
                entities = [project_entity] + entities
        else:
            entities = self.graph
        
        # 根据格式导出
        if format == "jsonld":
            # JSON-LD格式（标准语义网格式）
            export_data = {
                "@context": self.context,
                "@graph": entities
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            # CSV格式（表格分析用）
            return self._export_csv(entities)
        
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _export_csv(self, entities: List[Dict]) -> str:
        """导出为CSV格式"""
        import io
        import csv
        
        if not entities:
            return ""
        
        output = io.StringIO()
        
        # 收集所有可能的字段
        fields = set()
        for e in entities:
            fields.update(e.keys())
        fields = sorted(list(fields))
        
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        
        # 简化数据（处理嵌套对象）
        for e in entities:
            row = {}
            for f in fields:
                val = e.get(f, '')
                if isinstance(val, dict):
                    row[f] = json.dumps(val, ensure_ascii=False)
                else:
                    row[f] = val
            writer.writerow(row)
        
        return output.getvalue()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        return {
            "total_entities": len(self.graph),
            "entity_types": {
                t: len(items) for t, items in self.type_index.items()
            },
            "projects": list(self.project_index.keys())
        }
