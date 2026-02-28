"""
生产Agent
"""
from app.agents.base import BaseAgent
from app.models.schemas import SceneType
from typing import Dict, Any


class ProductionAgent(BaseAgent):
    """生产阶段Agent - 任务管理、瓶颈识别、资源优化"""
    
    def __init__(self):
        super().__init__(SceneType.PRODUCTION)
    
    def _get_system_prompt(self) -> str:
        return """你是钢箱梁生产调度专家，擅长排产优化和瓶颈分析。

## 核心能力
1. 生产任务管理：查询进度、状态跟踪
2. 瓶颈识别：发现延期风险和产能瓶颈
3. 优先级建议：优化生产排序
4. 资源分配：人员、设备、物料优化

## 优化目标
1. 交付准时率最大化
2. 设备利用率最大化
3. 在制品库存最小化
4. 质量风险最小化

## 瓶颈识别规则
- 实际工时 > 标准工时 × 1.2 → 黄色预警
- 实际工时 > 标准工时 × 1.5 → 红色预警
- 设备故障停机 > 2小时 → 红色预警
- 质量问题返工率 > 5% → 黄色预警

## 输出要求
1. 明确当前瓶颈位置（工序/设备/班组）
2. 量化影响（延期天数/产能损失）
3. 给出具体调整建议（优先级/资源/班次）
4. 预测调整后效果
"""
    
    async def process(self, message: str, context: Dict, kg_data: Dict) -> Dict[str, Any]:
        """处理生产相关问题"""
        from app.services.kg_client import kg_client
        from app.services.llm_service import llm_service
        
        kg_text = kg_client.format_for_llm(kg_data)
        
        # 分析瓶颈（简单规则）
        bottleneck_info = self._analyze_bottleneck(kg_data)
        
        prompt = f"""{self.system_prompt}

## 知识图谱数据
{kg_text}

## 瓶颈分析
{bottleneck_info}

## 用户问题
{message}

请基于上述信息，提供生产优化建议。
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
    
    def _analyze_bottleneck(self, kg_data: Dict) -> str:
        """简单瓶颈分析"""
        if not kg_data or "@graph" not in kg_data:
            return "暂无数据"
        
        processes = [e for e in kg_data["@graph"] if e.get("@type") == "sb:Process"]
        bottlenecks = []
        
        for p in processes:
            std = float(p.get("sb:standardHours", 0) or 0)
            actual = float(p.get("sb:actualHours", 0) or 0)
            
            if std > 0 and actual > std * 1.2:
                ratio = actual / std
                bottlenecks.append(
                    f"{p.get('sb:processName', '')}: "
                    f"标准{std}h，实际{actual}h，"
                    f"延迟{ratio:.1%}"
                )
        
        return "\n".join(bottlenecks) if bottlenecks else "暂无瓶颈"
