"""
Agent基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models.schemas import SceneType, Evidence


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, scene: SceneType):
        self.scene = scene
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    async def process(self, message: str, context: Dict, kg_data: Dict) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户消息
            context: 上下文信息
            kg_data: 知识图谱数据
        
        Returns:
            包含content、evidence等的字典
        """
        pass
    
    def format_evidence(self, kg_data: Dict) -> List[Evidence]:
        """从知识图谱数据中提取证据"""
        evidence = []
        
        if not kg_data or "@graph" not in kg_data:
            return evidence
        
        for entity in kg_data["@graph"][:5]:  # 最多5条证据
            etype = entity.get("@type", "").replace("sb:", "")
            eid = entity.get("@id", "").replace("sb:", "")
            
            # 构建证据
            content_parts = []
            for k, v in entity.items():
                if not k.startswith("@") and k != "sb:projectId":
                    key = k.replace("sb:", "")
                    content_parts.append(f"{key}: {v}")
            
            evidence.append(Evidence(
                type="kg",
                source=eid,
                title=f"{etype} - {eid}",
                content="; ".join(content_parts[:3]),
                relevance=0.9
            ))
        
        return evidence
