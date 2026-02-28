"""
设计Agent
"""
from app.agents.base import BaseAgent
from app.models.schemas import SceneType
from typing import Dict, Any


class DesignAgent(BaseAgent):
    """设计阶段Agent - 提供模块化设计参考和优化建议"""
    
    def __init__(self):
        super().__init__(SceneType.DESIGN)
    
    def _get_system_prompt(self) -> str:
        return """你是钢箱梁设计专家助手，擅长结构优化和材料选型。

## 核心能力
1. 模块化设计参考：基于相似案例提供设计参数建议
2. 结构优化建议：针对具体工况提出优化方案
3. 材料选型建议：根据性能要求推荐材质
4. 标准规范查询：引用相关设计规范

## 设计原则
1. 安全性：满足承载力、稳定性、疲劳要求
2. 经济性：优化用钢量，减少加工难度
3. 可制造性：考虑加工工艺和装配可行性
4. 标准化：优先采用标准构件和连接

## 输出要求
1. 给出具体参数建议（带数值）
2. 说明设计依据（规范条款/案例参考）
3. 提示潜在风险（加工/装配/耐久性）
4. 提供2-3个备选方案（如适用）

## 引用格式
- 图谱数据：[图谱:实体类型:实体ID]
- 标准条款：[标准:标准号:条款]
"""
    
    async def process(self, message: str, context: Dict, kg_data: Dict) -> Dict[str, Any]:
        """处理设计相关问题"""
        # 构建提示词
        from app.services.kg_client import kg_client
        kg_text = kg_client.format_for_llm(kg_data)
        
        prompt = f"""{self.system_prompt}

## 知识图谱数据
{kg_text}

## 用户问题
{message}

请基于上述知识，提供专业的设计建议。如信息不足，请明确告知。
"""
        
        # 调用大模型
        from app.services.llm_service import llm_service
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await llm_service.chat(messages)
        
        # 提取证据
        evidence = self.format_evidence(kg_data)
        
        return {
            "content": response,
            "evidence": evidence,
            "scene": self.scene.value
        }
