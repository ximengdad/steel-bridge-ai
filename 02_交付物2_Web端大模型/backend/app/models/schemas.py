"""
Pydantic数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum


class SceneType(str, Enum):
    """场景类型"""
    DESIGN = "design"
    PRODUCTION = "production"
    QUALITY = "quality"
    ASSEMBLY = "assembly"


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Evidence(BaseModel):
    """证据/引用来源"""
    type: str = Field(..., description="证据类型：kg/doc/standard/calculation")
    source: str = Field(..., description="来源标识")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容摘要")
    relevance: float = Field(default=0.9, description="相关度0-1")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: MessageRole
    content: str
    evidence: Optional[List[Evidence]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: Optional[str] = None
    message: str = Field(..., description="用户消息")
    scene: SceneType = Field(default=SceneType.PRODUCTION, description="场景")
    context: Dict = Field(default_factory=dict, description="上下文信息")
    stream: bool = Field(default=False, description="是否流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: str
    role: MessageRole = MessageRole.ASSISTANT
    content: str
    scene: SceneType
    evidence: List[Evidence] = Field(default_factory=list)
    suggestions: List[Dict] = Field(default_factory=list)
    usage: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.now)


class SessionCreate(BaseModel):
    """创建会话"""
    scene: SceneType
    project_id: Optional[str] = None
    title: Optional[str] = None


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    scene: SceneType
    project_id: Optional[str]
    title: Optional[str]
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class ExportRequest(BaseModel):
    """导出请求"""
    session_id: str
    format: Literal["markdown", "docx", "pdf"] = "markdown"
    include_evidence: bool = True
