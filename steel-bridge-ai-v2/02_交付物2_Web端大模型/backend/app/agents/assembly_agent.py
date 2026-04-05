"""
装配Agent
"""
from typing import Dict
from app.agents.base import BaseAgent
from app.models.schemas import SceneType


class AssemblyAgent(BaseAgent):
    """装配阶段Agent - 流程指导、路径规划、问题参考"""
    
    def __init__(self):
        super().__init__(SceneType.ASSEMBLY)
    
    def _get_system_prompt(self) -> str:
        return """你是钢箱梁装配专家，擅长吊装方案设计和现场问题处理。

## 核心能力
1. 装配流程指导：步骤分解、关键控制点
2. 路径规划建议：吊装路径、障碍物避让
3. 问题解决方案：历史案例匹配
4. 安全风险提示：气象、设备、人员

## 安全原则
1. 气象限制：风速≥6级、能见度<200m禁止吊装
2. 设备限制：吊机载荷率≤80%
3. 人员安全：吊臂下严禁站人
4. 结构安全：临时支撑必须可靠

## 输出要求
1. 步骤清单（带顺序和关键控制点）
2. 路径描述（含障碍物避让）
3. 气象窗口建议
4. 风险提示和应急预案
"""
    
    async def process(self, message: str, context: Dict, kg_data: Dict):
        from app.services.kg_client import kg_client
        from app.services.llm_service import llm_service
        
        kg_text = kg_client.format_for_llm(kg_data)
        
        prompt = f"""{self.system_prompt}

## 知识图谱数据
{kg_text}

## 用户问题
{message}

请提供装配指导方案。
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await llm_service.chat(messages)
        evidence = self.format_evidence(kg_data)
        
        return {
            "content": response,
            "evidence": evidence,
            "scene": self.scene.value
        }
