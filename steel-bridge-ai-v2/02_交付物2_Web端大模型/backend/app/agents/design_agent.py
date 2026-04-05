"""
设计Agent - 柳林桥专用
提供基于真实图纸数据的设计参考和优化建议
"""
from app.agents.base import BaseAgent
from app.models.schemas import SceneType
from typing import Dict, Any
import json
import os


class DesignAgent(BaseAgent):
    """设计阶段Agent - 基于柳林桥真实数据提供设计参考"""
    
    def __init__(self):
        super().__init__(SceneType.DESIGN)
        self.kg_data = self._load_kg_data()
    
    def _load_kg_data(self) -> Dict:
        """加载柳林桥知识图谱数据"""
        try:
            # 尝试从相对路径加载
            kg_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', '..', 
                '01_交付物1_知识图谱服务', 
                'data', 
                'kg_liulin_bridge.jsonld'
            )
            with open(kg_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _get_system_prompt(self) -> str:
        return """你是柳林桥钢箱梁设计专家助手，基于真实图纸数据提供专业建议。

## 项目背景
- 项目名称：柳林桥钢箱梁建造项目
- 桥型：中承式拱桥（钢箱梁）
- 地点：天津市
- 设计单位：中交第一航务工程局

## 核心能力
1. **图纸查询**：根据构件名称查找对应图纸编号
2. **参数解读**：解释图纸中的技术参数
3. **设计优化**：基于柳林桥实际案例提供优化建议
4. **规范引用**：引用相关设计规范（JTG D64-2015等）

## 柳林桥主要构件系统
1. **下部结构系统**：桥墩、桩基础、承台、支座系统
2. **拱肋结构系统**：
   - 主拱Z1-Z10（10节段）
   - 次拱C1-C5（5节段）
   - 横撑HC1-HC2
3. **主梁系统**：主梁节段、拱梁结合段、预拱度设计
4. **吊索系统**：吊索布置及构造
5. **桥面系及附属设施**：桥面铺装、防撞护栏、排水管、伸缩缝、路灯
6. **智慧桥梁系统**：传感器布设、测点布置、健康监测

## 关键图纸索引
- 拱肋节段划分：S2-1-2-2、3
- 主拱Z1构造：S2-1-2-5
- 主拱Z2,Z4-Z10：S2-1-2-6,8～14
- 主拱Z3构造：S2-1-2-7
- 次拱C1-C5：S2-1-2-15~19
- 拱肋横撑：S2-1-2-20, S2-1-2-22 23
- 主梁梁段划分：S2-1-3-2
- 主梁节段构造：S2-1-3-5~7
- 吊索布置：S2-1-4-1

## 输出要求
1. 给出具体图纸编号引用
2. 说明设计依据（规范条款/案例参考）
3. 提示关键参数（尺寸、材料、预拱度等）
4. 提供柳林桥类似案例参考

## 引用格式
- 图纸引用：[图纸:图号:图名]
- 规范引用：[规范:标准号:条款]
- 构件引用：[构件:系统:构件名]
"""
    
    async def process(self, message: str, context: Dict, kg_data: Dict) -> Dict[str, Any]:
        """处理设计相关问题"""
        message_lower = message.lower()
        
        # 基于关键词匹配提供快速响应
        response = {
            "content": "",
            "evidence": [],
            "scene": self.scene.value,
            "related_drawings": [],
            "suggestions": []
        }
        
        # 拱肋相关查询
        if "拱肋" in message or "拱" in message:
            response["content"] = self._get_arch_design_info(message)
            response["related_drawings"] = [
                {"drawingNo": "S2-1-2-2、3", "drawingName": "拱肋节段划分及控制坐标总图"},
                {"drawingNo": "S2-1-2-5", "drawingName": "主拱Z1节段构造"},
                {"drawingNo": "S2-1-2-7", "drawingName": "主拱Z3节段构造"},
                {"drawingNo": "S2-1-2-15~19", "drawingName": "次拱C1-C5节段构造"}
            ]
            response["suggestions"] = [
                "查看图纸 S2-1-2-4 了解预拱度布置要求",
                "参考 S2-1-9 焊缝设计图",
                "注意拱肋节段间的工地连接构造"
            ]
        
        # 主梁相关查询
        elif "主梁" in message or "梁段" in message:
            response["content"] = self._get_beam_design_info(message)
            response["related_drawings"] = [
                {"drawingNo": "S2-1-3-2", "drawingName": "主梁梁段划分图"},
                {"drawingNo": "S2-1-3-4", "drawingName": "主梁预拱度布置"},
                {"drawingNo": "S2-1-3-5~7", "drawingName": "主梁节段构造"},
                {"drawingNo": "S2-1-3-8~9", "drawingName": "主梁拱梁结合段构造"}
            ]
            response["suggestions"] = [
                "预拱度设置需符合设计要求",
                "拱梁结合段是结构关键部位",
                "参考焊缝设计图 S2-1-9"
            ]
        
        # 图纸查询
        elif "图纸" in message:
            response["content"] = self._get_drawing_info(message)
            response["suggestions"] = [
                "使用 /drawings/search 接口搜索具体图纸",
                "按分类查看：下部结构、拱肋结构、主梁系统、桥面系、智慧桥梁",
                "图纸总计72张，其中主桥64张"
            ]
        
        else:
            # 通用设计建议
            response["content"] = """柳林桥为中承式拱桥钢箱梁结构，我可以为您提供以下设计相关建议：

**主要构件系统：**
1. **下部结构**：桥墩、桩基础、承台、支座
2. **拱肋结构**：主拱Z1-Z10、次拱C1-C5、横撑
3. **主梁系统**：主梁节段、拱梁结合段
4. **吊索系统**：吊索布置及张拉
5. **桥面系**：铺装、护栏、排水、伸缩缝

**请告诉我您具体想了解：**
- 某个构件的图纸编号
- 构件的详细参数
- 设计规范和标准
- 施工建议"""
        
        return response
    
    def _get_arch_design_info(self, message: str) -> str:
        """获取拱肋设计信息"""
        return """## 柳林桥拱肋结构设计信息

### 结构组成
- **主拱**：Z1-Z10 共10个节段
  - Z1：拱脚起始节段（图纸 S2-1-2-5）
  - Z2,Z4-Z10：标准节段（图纸 S2-1-2-6,8～14）
  - Z3：拱顶节段（图纸 S2-1-2-7）
- **次拱**：C1-C5 共5个节段（图纸 S2-1-2-15~19）
- **横撑**：HC1、HC2（图纸 S2-1-2-22 23）

### 关键设计参数
- **预拱度**：详见图纸 S2-1-2-4
- **节段划分**：详见图纸 S2-1-2-2、3
- **焊缝设计**：详见图纸 S2-1-9

### 设计要点
1. 拱肋采用钢箱梁结构，分段制作、现场拼装
2. 预拱度设置需抵消施工和运营阶段的变形
3. 节段间采用工地焊接连接（图纸 S2-1-2-25）
4. 临时吊点构造详见 S2-1-2-24

### 相关规范
- [规范:JTG D64-2015:公路钢结构桥梁设计规范]
- [规范:GB 50661-2011:钢结构焊接规范]"""
    
    def _get_beam_design_info(self, message: str) -> str:
        """获取主梁设计信息"""
        return """## 柳林桥主梁系统设计信息

### 结构组成
- **主梁节段**：根据图纸 S2-1-3-2 划分
- **拱梁结合段**：主梁与拱肋连接部位（图纸 S2-1-3-8~9）
- **预拱度**：详见图纸 S2-1-3-4

### 关键设计参数
- **材料**：钢箱梁结构
- **梁段划分**：根据运输和吊装能力确定
- **预拱度**：按设计计算确定，抵消恒载和活载变形

### 设计要点
1. 主梁采用钢箱梁，分段预制
2. 拱梁结合段是结构受力的关键部位，需重点加强
3. 预拱度设置需符合 S2-1-3-4 要求
4. 临时吊点构造详见 S2-1-3-10 11 12

### 相关图纸
- [图纸:S2-1-3-2:主梁梁段划分图]
- [图纸:S2-1-3-4:主梁预拱度布置]
- [图纸:S2-1-3-5~7:主梁节段构造]
- [图纸:S2-1-3-8~9:主梁拱梁结合段构造]"""
    
    def _get_drawing_info(self, message: str) -> str:
        """获取图纸信息"""
        return """## 柳林桥图纸清单

### 图纸统计
- **总计**：72张图纸
- **主桥图纸**：64张
- **智慧桥梁**：4张

### 分类明细
1. **下部结构**（约10张）
   - S2-1-1-1 ~ S2-1-1-11：基础、墩身、支座等

2. **拱肋结构**（约15张）
   - S2-1-2-1 ~ S2-1-2-28：主拱、次拱、横撑、临时结构

3. **主梁系统**（约8张）
   - S2-1-3-1 ~ S2-1-3-13：梁段划分、节段构造、结合段

4. **吊索系统**（约2张）
   - S2-1-4-1：吊索布置及构造

5. **桥面系**（约10张）
   - S2-1-5-1 ~ S2-1-5-11：铺装、护栏、排水、伸缩缝

6. **智慧桥梁**（4张）
   - C8-01 ~ C8-04~34：传感器、测点布置、供电传输

### 查询方式
- 按图号查询：/drawings/{drawing_no}
- 按分类查询：/drawings/category/{category}
- 关键词搜索：/drawings/search?keyword=xxx"""
    
    def format_evidence(self, kg_data: Dict) -> List[Dict]:
        """格式化证据"""
        evidence = []
        graph = kg_data.get('@graph', [])
        
        for entity in graph:
            if 'Drawing' in entity.get('@type', ''):
                evidence.append({
                    "type": "drawing",
                    "drawingNo": entity.get('sb:drawingNo'),
                    "drawingName": entity.get('sb:drawingName'),
                    "category": entity.get('sb:category')
                })
        
        return evidence[:5]  # 最多返回5条证据
