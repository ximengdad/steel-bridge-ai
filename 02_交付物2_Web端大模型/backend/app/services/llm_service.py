"""
大模型服务
"""
import os
from typing import List, Dict, AsyncGenerator
from openai import AsyncOpenAI
from app.config import (
    LLM_TYPE, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL,
    LOCAL_MODEL_URL, LOCAL_MODEL_NAME, MAX_CONTEXT_LENGTH
)


class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        if LLM_TYPE == "openai":
            self.client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL
            )
            self.model = OPENAI_MODEL
        else:
            # 本地模型（vLLM等）
            self.client = AsyncOpenAI(
                api_key="not-needed",
                base_url=LOCAL_MODEL_URL
            )
            self.model = LOCAL_MODEL_NAME
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> str:
        """
        对话生成
        
        Args:
            messages: 消息列表
            temperature: 温度（创造性）
            max_tokens: 最大token数
            stream: 是否流式输出
        
        Returns:
            生成的文本
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return response  # 返回流式迭代器
            else:
                return response.choices[0].message.content
        
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return f"抱歉，模型调用失败：{str(e)}"
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """流式对话"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"错误：{str(e)}"


# 全局服务实例
llm_service = LLMService()
