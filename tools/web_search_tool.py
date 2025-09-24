"""
Web搜索工具
当Tavily不可用时的备用搜索方案
"""

import requests
from typing import List, Dict
import logging

# 兼容性导入 - 支持不同版本的LangChain
try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.tools import tool
    except ImportError:
        # 如果LangChain不可用，创建一个简单的装饰器
        def tool(name):
            def decorator(func):
                func._name = name
                return func
            return decorator

logger = logging.getLogger(__name__)


@tool("BasicWebSearchTool")
def basic_web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    基础Web搜索工具（备用方案）
    
    Args:
        query (str): 搜索查询词
        max_results (int): 最大返回结果数量
    
    Returns:
        List[Dict]: 搜索结果列表
    """
    try:
        # 这是一个简化的搜索实现
        # 在实际使用中，您可能需要使用Google Custom Search API或其他搜索服务
        
        logger.info(f"执行基础Web搜索: {query}")
        
        # 模拟搜索结果
        results = [
            {
                "title": f"关于 '{query}' 的搜索结果",
                "content": f"这是一个关于 {query} 的模拟搜索结果。在实际部署中，您需要配置真实的Web搜索API。",
                "url": f"https://example.com/search?q={query.replace(' ', '+')}"
            }
        ]
        
        logger.info(f"基础搜索返回 {len(results)} 个结果")
        return results
        
    except Exception as e:
        logger.error(f"基础Web搜索失败: {str(e)}")
        return [{"error": f"搜索失败: {str(e)}"}]


@tool("MockTavilySearchTool") 
def mock_tavily_search(query: str) -> str:
    """
    模拟Tavily搜索的备用工具
    
    Args:
        query (str): 搜索查询
        
    Returns:
        str: 格式化的搜索结果
    """
    try:
        logger.info(f"使用模拟Tavily搜索: {query}")
        
        # 提供基础的搜索建议
        result = f"""
基于查询 "{query}" 的搜索结果：

注意：当前使用的是模拟搜索工具。为了获得真实的Web搜索结果，请：
1. 确保安装了 tavily-python 包
2. 在.env文件中配置 TAVILY_API_KEY
3. 重新启动应用

建议的研究方向：
- 查阅相关的学术论文和技术文档
- 关注该领域的最新发展趋势
- 寻找权威机构和专家的观点
- 了解实际应用案例和产业动态

如果需要进行实际的Web搜索，请手动搜索相关信息并提供给系统。
"""
        
        return result
        
    except Exception as e:
        logger.error(f"模拟搜索失败: {str(e)}")
        return f"搜索失败: {str(e)}"
