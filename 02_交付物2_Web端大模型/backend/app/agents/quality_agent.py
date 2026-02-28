"""
质检Agent
"""
from app.agents.base import BaseAgent
from app.models.schemas import SceneType


class QualityAgent(BaseAgent):
    """质检阶段Agent - 缺陷分析、原因推断、改进建议"""
    
    def __init__(self):
        super().__init__(SceneType.QUALITY)
    
    def _get_system_prompt(self) -> str:
        return """你是钢箱梁质量专家，擅长缺陷分析和根因推断。

## 核心能力
1. 缺陷智能分析：基于描述识别缺陷类型
2. 原因推断：分析人、机、料、法、环、测
3. 改进建议：提供针对性预防措施
4. 历史案例匹配：查找相似缺陷

## 缺陷分类
- A类（严重）：影响结构安全，必须返工
- B类（一般）：影响外观或耐久，可返修
- C类（轻微）：不影响性能，可让步接收

## 分析原则
1. 基于事实：依据检测数据和历史案例
2. 系统思维：考虑人、机、料、法、环、测
3. 预防为主：解决当前问题并预防再发
4. 标准合规：符合GB/T 714、TB/T 2658等标准

## 输出要求
1. 缺陷定级（A/B/C类）
2. 可能原因列表（按概率排序）
3. 处置建议（返工/返修/让步）
4. 预防措施（针对性）
"""
    
    async def process(self, message: str, context: Dict, kg_data: Dict):
        from app.services.kg_client import kg_client
        from app.services.llm_service import llm_service
        
        kg_text = kg_client.format_for_llm(kg_data)
        
        prompt = f"""{self.system_prompt}

## 知识图谱数据（历史缺陷案例）
{kg_text}

## 用户问题
{message}

请分析质量问题，提供原因推断和改进建议。
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
