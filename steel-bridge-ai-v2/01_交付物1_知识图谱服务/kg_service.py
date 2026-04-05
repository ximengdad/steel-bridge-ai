"""
柳林桥知识图谱服务
支持图纸检索、构件查询、施工建议生成
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class LiuLinBridgeKG:
    """柳林桥知识图谱服务"""
    
    def __init__(self, data_path: str = None):
        """
        初始化知识图谱
        
        Args:
            data_path: JSON-LD数据文件路径，默认使用kg_liulin_bridge.jsonld
        """
        if data_path is None:
            # 获取当前文件所在目录
            current_dir = Path(__file__).parent
            data_path = current_dir / "data" / "kg_liulin_bridge.jsonld"
        
        self.data_path = Path(data_path)
        self.graph = []
        self.context = {}
        self.drawings_index = {}  # 图纸索引
        self.components_index = {}  # 构件索引
        self.processes_index = {}  # 工序索引
        self.specs_index = {}  # 规范索引
        
        self._load_data()
        self._build_indexes()
    
    def _load_data(self):
        """加载JSON-LD数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.context = data.get('@context', {})
            self.graph = data.get('@graph', [])
            
            print(f"✅ 柳林桥知识图谱加载成功: {len(self.graph)} 个实体")
            
            # 统计各类实体
            stats = self.get_statistics()
            print(f"  - 图纸: {stats.get('drawings_count', 0)} 张")
            print(f"  - 构件系统: {stats.get('systems_count', 0)} 个")
            print(f"  - 工序: {stats.get('processes_count', 0)} 个")
            print(f"  - 规范: {stats.get('specs_count', 0)} 个")
            
        except FileNotFoundError:
            print(f"⚠️ 警告: 数据文件不存在 {self.data_path}")
            self.graph = []
        except json.JSONDecodeError as e:
            print(f"❌ 错误: JSON解析失败 - {e}")
            self.graph = []
    
    def _build_indexes(self):
        """构建索引以加速查询"""
        for entity in self.graph:
            entity_id = entity.get('@id', '')
            entity_type = entity.get('@type', '')
            
            # 图纸索引
            if 'Drawing' in entity_type:
                drawing_no = entity.get('sb:drawingNo', '')
                if drawing_no:
                    self.drawings_index[drawing_no] = entity
                # 按分类索引
                category = entity.get('sb:category', '')
                if category:
                    if category not in self.drawings_index:
                        self.drawings_index[category] = []
                    self.drawings_index[category].append(entity)
            
            # 构件索引
            elif 'ComponentSystem' in entity_type:
                system_name = entity.get('sb:systemName', '')
                if system_name:
                    self.components_index[system_name] = entity
            
            # 工序索引
            elif 'ConstructionProcess' in entity_type:
                process_name = entity.get('sb:processName', '')
                if process_name:
                    self.processes_index[process_name] = entity
            
            # 规范索引
            elif 'TechnicalSpecification' in entity_type:
                spec_id = entity.get('sb:specId', '')
                if spec_id:
                    self.specs_index[spec_id] = entity
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        stats = {
            "total_entities": len(self.graph),
            "drawings_count": 0,
            "systems_count": 0,
            "processes_count": 0,
            "specs_count": 0,
            "categories": set()
        }
        
        for entity in self.graph:
            entity_type = entity.get('@type', '')
            
            if 'Drawing' in entity_type:
                stats['drawings_count'] += 1
                category = entity.get('sb:category', '')
                if category:
                    stats['categories'].add(category)
            elif 'ComponentSystem' in entity_type:
                stats['systems_count'] += 1
            elif 'ConstructionProcess' in entity_type:
                stats['processes_count'] += 1
            elif 'TechnicalSpecification' in entity_type:
                stats['specs_count'] += 1
        
        stats['categories'] = list(stats['categories'])
        return stats
    
    def get_by_id(self, entity_id: str) -> Optional[Dict]:
        """根据ID获取实体"""
        for entity in self.graph:
            if entity.get('@id') == entity_id:
                return entity
        return None
    
    def query_drawings(self, category: str = None, component: str = None, keyword: str = None) -> List[Dict]:
        """
        查询图纸
        
        Args:
            category: 图纸分类（如：下部结构、拱肋结构、主梁系统等）
            component: 关联构件
            keyword: 关键词搜索
        
        Returns:
            图纸列表
        """
        results = []
        
        for entity in self.graph:
            if 'Drawing' not in entity.get('@type', ''):
                continue
            
            # 分类筛选
            if category and entity.get('sb:category') != category:
                continue
            
            # 构件筛选
            if component:
                related = entity.get('sb:relatedComponents', [])
                if component not in related:
                    continue
            
            # 关键词搜索
            if keyword:
                keyword_lower = keyword.lower()
                searchable = [
                    entity.get('sb:drawingNo', ''),
                    entity.get('sb:drawingName', ''),
                    entity.get('sb:category', '')
                ]
                if not any(keyword_lower in str(s).lower() for s in searchable):
                    continue
            
            results.append(entity)
        
        return results
    
    def get_drawing_by_no(self, drawing_no: str) -> Optional[Dict]:
        """根据图号获取图纸信息"""
        return self.drawings_index.get(drawing_no)
    
    def get_component_system(self, system_name: str) -> Optional[Dict]:
        """获取构件系统信息"""
        return self.components_index.get(system_name)
    
    def get_construction_process(self, process_name: str) -> Optional[Dict]:
        """获取施工工序信息"""
        return self.processes_index.get(process_name)
    
    def get_all_drawings_by_category(self) -> Dict[str, List[Dict]]:
        """按分类获取所有图纸"""
        categories = {}
        for entity in self.graph:
            if 'Drawing' in entity.get('@type', ''):
                category = entity.get('sb:category', '其他')
                if category not in categories:
                    categories[category] = []
                categories[category].append(entity)
        return categories
    
    def search_drawings(self, query: str) -> List[Dict]:
        """搜索图纸（支持模糊匹配）"""
        results = []
        query_lower = query.lower()
        
        for entity in self.graph:
            if 'Drawing' not in entity.get('@type', ''):
                continue
            
            # 搜索多个字段
            searchable_fields = [
                entity.get('sb:drawingNo', ''),
                entity.get('sb:drawingName', ''),
                entity.get('sb:category', ''),
                entity.get('sb:filePath', '')
            ]
            
            if any(query_lower in str(field).lower() for field in searchable_fields):
                results.append(entity)
        
        return results
    
    def get_related_drawings(self, component_id: str) -> List[Dict]:
        """获取与指定构件相关的所有图纸"""
        results = []
        for entity in self.graph:
            if 'Drawing' in entity.get('@type', ''):
                related = entity.get('sb:relatedComponents', [])
                if component_id in related:
                    results.append(entity)
        return results
    
    def get_construction_guide(self, component_name: str) -> Dict[str, Any]:
        """
        获取构件的施工指导
        
        Returns:
            包含工序、图纸、规范的综合指导
        """
        guide = {
            "component": component_name,
            "drawings": [],
            "processes": [],
            "specs": []
        }
        
        # 查找相关图纸
        for entity in self.graph:
            if 'Drawing' in entity.get('@type', ''):
                related = entity.get('sb:relatedComponents', [])
                if any(component_name in r for r in related):
                    guide['drawings'].append({
                        "drawingNo": entity.get('sb:drawingNo'),
                        "drawingName": entity.get('sb:drawingName'),
                        "filePath": entity.get('sb:filePath')
                    })
            
            # 查找相关工序
            elif 'ConstructionProcess' in entity.get('@type', ''):
                if component_name in entity.get('sb:description', ''):
                    guide['processes'].append({
                        "processId": entity.get('sb:processId'),
                        "processName": entity.get('sb:processName'),
                        "description": entity.get('sb:description'),
                        "standardHours": entity.get('sb:standardHours'),
                        "relatedDrawings": entity.get('sb:relatedDrawings', [])
                    })
        
        return guide
    
    def get_sketch_params(self, sketch_type: str) -> Dict[str, Any]:
        """
        获取施工草图参数
        
        Args:
            sketch_type: 草图类型（arch_installation, beam_fabrication, deck_construction等）
        
        Returns:
            草图参数
        """
        sketch_params = {
            "arch_installation": {
                "title": "拱肋安装施工草图",
                "components": ["主拱Z1-Z10", "次拱C1-C5", "横撑HC1-HC2"],
                "steps": [
                    "桥墩基础施工完成",
                    "拱脚预埋件安装",
                    "Z1节段吊装就位",
                    "Z2-Z10依次对称吊装",
                    "次拱C1-C5安装",
                    "横撑连接",
                    "工地焊接"
                ],
                "key_drawings": ["S2-1-2-2、3", "S2-1-2-24", "S2-1-2-25", "S2-1-2-26"],
                "notes": ["注意预拱度控制", "对称安装", "临时连接牢固"]
            },
            "beam_fabrication": {
                "title": "主梁节段制作草图",
                "components": ["主梁节段", "拱梁结合段"],
                "steps": [
                    "钢板数控切割",
                    "边缘加工坡口",
                    "组对定位",
                    "焊接（分段跳焊）",
                    "预拱度调整",
                    "焊缝检测"
                ],
                "key_drawings": ["S2-1-3-2", "S2-1-3-4", "S2-1-3-5~7", "S2-1-9"],
                "notes": ["控制焊接变形", "预拱度按设计要求", "焊缝质量100%检测"]
            },
            "deck_construction": {
                "title": "桥面系施工草图",
                "components": ["桥面铺装", "防撞护栏", "排水管", "伸缩缝"],
                "steps": [
                    "主梁涂装完成",
                    "桥面防水层施工",
                    "沥青混凝土铺装",
                    "防撞护栏安装",
                    "排水系统连接",
                    "伸缩缝安装"
                ],
                "key_drawings": ["S2-1-5-3", "S2-1-5-4", "S2-1-5-5", "S2-1-5-11"],
                "notes": ["防水是关键", "护栏线形顺直", "排水坡度正确"]
            }
        }
        
        return sketch_params.get(sketch_type, {})
    
    def export(self, format: str = "jsonld", category: str = None) -> str:
        """导出知识图谱数据"""
        if format == "jsonld":
            data = {
                "@context": self.context,
                "@graph": self.graph
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            # 简化的CSV导出
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Type', 'Name', 'Category', 'FilePath'])
            
            for entity in self.graph:
                writer.writerow([
                    entity.get('@id', ''),
                    entity.get('@type', ''),
                    entity.get('sb:drawingName', entity.get('sb:systemName', '')),
                    entity.get('sb:category', ''),
                    entity.get('sb:filePath', '')
                ])
            
            return output.getvalue()
        
        return ""


if __name__ == "__main__":
    # 测试
    kg = LiuLinBridgeKG()
    
    print("\n=== 图纸分类统计 ===")
    categories = kg.get_all_drawings_by_category()
    for cat, drawings in categories.items():
        print(f"{cat}: {len(drawings)} 张")
    
    print("\n=== 搜索图纸 '拱肋' ===")
    results = kg.search_drawings("拱肋")
    for d in results[:3]:
        print(f"  {d.get('sb:drawingNo')}: {d.get('sb:drawingName')}")
    
    print("\n=== 获取拱肋安装施工指导 ===")
    guide = kg.get_construction_guide("sb:ArchRib_System")
    print(f"  图纸数量: {len(guide['drawings'])}")
    print(f"  工序数量: {len(guide['processes'])}")
    
    print("\n=== 施工草图参数 ===")
    sketch = kg.get_sketch_params("arch_installation")
    print(f"  标题: {sketch.get('title')}")
    print(f"  步骤: {len(sketch.get('steps', []))} 步")
