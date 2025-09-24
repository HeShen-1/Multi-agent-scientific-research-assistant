"""
记忆工具 - 长期记忆与知识库功能
实现研究历史的存储、检索和利用
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain.tools import tool


class ResearchMemory:
    """研究记忆管理器"""
    
    def __init__(self, persist_directory: str = ".memory"):
        """
        初始化记忆管理器
        
        Args:
            persist_directory: 数据持久化目录
        """
        self.persist_directory = persist_directory
        self.ensure_directory()
        
        # 初始化ChromaDB客户端
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 创建或获取集合
            self.collection = self.client.get_or_create_collection(
                name="research_memory",
                metadata={"description": "研究报告和知识的长期存储"}
            )
            
            print(f"✅ 记忆数据库初始化成功: {self.persist_directory}")
            
        except Exception as e:
            print(f"⚠️ ChromaDB初始化失败，使用简化内存模式: {e}")
            self.client = None
            self.collection = None
            self._fallback_memory = {}
    
    def ensure_directory(self):
        """确保记忆目录存在"""
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # 创建元数据文件
        metadata_file = Path(self.persist_directory) / "metadata.json"
        if not metadata_file.exists():
            metadata = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "多智能体科研助手记忆数据库"
            }
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def generate_memory_id(self, topic: str, timestamp: str = None) -> str:
        """生成记忆ID"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        content = f"{topic}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def store_research(self, 
                      topic: str, 
                      content: str, 
                      metadata: Dict[str, Any] = None) -> str:
        """
        存储研究报告到记忆库
        
        Args:
            topic: 研究主题
            content: 报告内容
            metadata: 额外元数据
            
        Returns:
            str: 记忆ID
        """
        timestamp = datetime.now().isoformat()
        memory_id = self.generate_memory_id(topic, timestamp)
        
        # 准备元数据
        full_metadata = {
            "topic": topic,
            "timestamp": timestamp,
            "content_length": len(content),
            "memory_id": memory_id,
            **(metadata or {})
        }
        
        try:
            if self.collection is not None:
                # 使用ChromaDB存储
                self.collection.add(
                    documents=[content],
                    metadatas=[full_metadata],
                    ids=[memory_id]
                )
                
                print(f"📚 研究记忆已存储: {memory_id} - {topic[:50]}...")
                
            else:
                # 降级到内存存储
                self._fallback_memory[memory_id] = {
                    "content": content,
                    "metadata": full_metadata
                }
                print(f"📝 研究记忆已临时存储: {memory_id}")
                
        except Exception as e:
            print(f"❌ 存储记忆失败: {e}")
            return ""
        
        return memory_id
    
    def search_memories(self, 
                       query: str, 
                       n_results: int = 3,
                       relevance_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        搜索相关的历史研究
        
        Args:
            query: 搜索查询
            n_results: 返回结果数量
            relevance_threshold: 相关性阈值
            
        Returns:
            List[Dict]: 相关的历史研究列表
        """
        try:
            if self.collection is not None:
                # 使用ChromaDB搜索
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"]
                )
                
                memories = []
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i] if "distances" in results else 0
                    
                    # 计算相关性分数 (1 - distance)
                    relevance = max(0, 1 - distance)
                    
                    if relevance >= relevance_threshold:
                        memories.append({
                            "content": doc,
                            "metadata": metadata,
                            "relevance": relevance,
                            "memory_id": metadata.get("memory_id", "unknown")
                        })
                
                return sorted(memories, key=lambda x: x["relevance"], reverse=True)
                
            else:
                # 降级到简单文本匹配
                memories = []
                for memory_id, memory_data in self._fallback_memory.items():
                    content = memory_data["content"]
                    metadata = memory_data["metadata"]
                    
                    # 简单的关键词匹配
                    query_lower = query.lower()
                    content_lower = content.lower()
                    topic_lower = metadata.get("topic", "").lower()
                    
                    if query_lower in content_lower or query_lower in topic_lower:
                        memories.append({
                            "content": content,
                            "metadata": metadata,
                            "relevance": 0.8,  # 固定相关性分数
                            "memory_id": memory_id
                        })
                
                return memories[:n_results]
                
        except Exception as e:
            print(f"❌ 搜索记忆失败: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆库统计信息"""
        try:
            if self.collection is not None:
                count = self.collection.count()
                return {
                    "total_memories": count,
                    "storage_type": "ChromaDB",
                    "persist_directory": self.persist_directory
                }
            else:
                count = len(self._fallback_memory)
                return {
                    "total_memories": count,
                    "storage_type": "Memory (Fallback)",
                    "persist_directory": self.persist_directory
                }
        except Exception as e:
            return {
                "total_memories": 0,
                "storage_type": "Error",
                "error": str(e)
            }
    
    def clear_memories(self, confirm: bool = False) -> bool:
        """清空所有记忆（危险操作）"""
        if not confirm:
            print("⚠️ 需要确认才能清空记忆库")
            return False
        
        try:
            if self.collection is not None:
                self.client.delete_collection("research_memory")
                self.collection = self.client.create_collection(
                    name="research_memory",
                    metadata={"description": "研究报告和知识的长期存储"}
                )
            else:
                self._fallback_memory.clear()
            
            print("🧹 记忆库已清空")
            return True
            
        except Exception as e:
            print(f"❌ 清空记忆库失败: {e}")
            return False


# 全局记忆管理器实例
_global_memory = None

def get_memory_manager() -> ResearchMemory:
    """获取全局记忆管理器实例"""
    global _global_memory
    if _global_memory is None:
        _global_memory = ResearchMemory()
    return _global_memory


@tool("recall_past_research")
def recall_past_research(query: str, max_results: int = 3) -> str:
    """
    查询历史研究知识库，寻找与当前主题相关的过往研究。
    
    Args:
        query: 搜索查询，描述要查找的研究主题或技术
        max_results: 最大返回结果数量
        
    Returns:
        str: 格式化的历史研究摘要
    """
    try:
        memory_manager = get_memory_manager()
        memories = memory_manager.search_memories(query, n_results=max_results)
        
        if not memories:
            return f"📭 未找到与 '{query}' 相关的历史研究记录。"
        
        # 格式化输出
        result = f"📚 找到 {len(memories)} 条相关的历史研究：\n\n"
        
        for i, memory in enumerate(memories, 1):
            metadata = memory["metadata"]
            relevance = memory["relevance"]
            
            topic = metadata.get("topic", "未知主题")
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                date_str = timestamp.split("T")[0]  # 提取日期部分
            else:
                date_str = "未知日期"
            
            # 截取内容摘要
            content_preview = memory["content"][:200] + "..." if len(memory["content"]) > 200 else memory["content"]
            
            result += f"### {i}. {topic}\n"
            result += f"**日期**: {date_str} | **相关性**: {relevance:.2f}\n"
            result += f"**摘要**: {content_preview}\n\n"
        
        result += "---\n💡 提示：基于以上历史研究，您可以避免重复工作并建立在已有基础上。"
        
        return result
        
    except Exception as e:
        return f"❌ 查询历史研究时发生错误: {str(e)}"


@tool("store_research_memory")
def store_research_memory(topic: str, content: str, additional_info: str = "") -> str:
    """
    将当前研究存储到长期记忆库。
    
    Args:
        topic: 研究主题
        content: 研究内容或报告
        additional_info: 额外信息（如执行模式、耗时等）
        
    Returns:
        str: 存储结果信息
    """
    try:
        memory_manager = get_memory_manager()
        
        # 准备元数据
        metadata = {}
        if additional_info:
            metadata["additional_info"] = additional_info
        
        memory_id = memory_manager.store_research(topic, content, metadata)
        
        if memory_id:
            stats = memory_manager.get_memory_stats()
            return f"✅ 研究已成功存储到记忆库\n记忆ID: {memory_id}\n当前记忆库总数: {stats['total_memories']}"
        else:
            return "❌ 研究存储失败"
            
    except Exception as e:
        return f"❌ 存储研究记忆时发生错误: {str(e)}"


@tool("memory_stats")
def memory_stats() -> str:
    """
    获取记忆库统计信息。
    
    Returns:
        str: 记忆库统计信息
    """
    try:
        memory_manager = get_memory_manager()
        stats = memory_manager.get_memory_stats()
        
        result = "📊 记忆库统计信息：\n"
        result += f"- 总记忆数量: {stats['total_memories']}\n"
        result += f"- 存储类型: {stats['storage_type']}\n"
        result += f"- 存储路径: {stats['persist_directory']}\n"
        
        if "error" in stats:
            result += f"- 错误信息: {stats['error']}\n"
        
        return result
        
    except Exception as e:
        return f"❌ 获取记忆库统计信息时发生错误: {str(e)}"


# 导出主要工具
__all__ = [
    "ResearchMemory",
    "get_memory_manager", 
    "recall_past_research",
    "store_research_memory",
    "memory_stats"
]
