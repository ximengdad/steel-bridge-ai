from app.agents.design_agent import DesignAgent
from app.agents.production_agent import ProductionAgent
from app.agents.quality_agent import QualityAgent
from app.agents.assembly_agent import AssemblyAgent
from app.models.schemas import SceneType

# Agent工厂
AGENT_MAP = {
    SceneType.DESIGN: DesignAgent,
    SceneType.PRODUCTION: ProductionAgent,
    SceneType.QUALITY: QualityAgent,
    SceneType.ASSEMBLY: AssemblyAgent
}


def get_agent(scene: SceneType):
    """获取对应场景的Agent"""
    agent_class = AGENT_MAP.get(scene)
    if agent_class:
        return agent_class()
    return ProductionAgent()  # 默认
