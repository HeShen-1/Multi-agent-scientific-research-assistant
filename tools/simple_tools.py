"""
简单工具定义
使用字典形式定义工具，避免CrewAI验证问题
"""

import arxiv
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def arxiv_search_function(query: str, max_results: int = 5) -> str:
    """
    arXiv搜索函数
    
    Args:
        query: 搜索查询词
        max_results: 最大结果数量
    
    Returns:
        str: 格式化的搜索结果
    """
    try:
        logger.info(f"开始搜索arXiv，查询: {query}")
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        results = []
        for result in client.results(search):
            paper_info = (
                f"**标题**: {result.title.strip()}\n"
                f"**作者**: {', '.join([author.name for author in result.authors[:3]])}{'...' if len(result.authors) > 3 else ''}\n"
                f"**发布日期**: {result.published.strftime('%Y-%m-%d')}\n"
                f"**摘要**: {result.summary.strip().replace(chr(10), ' ')[:300]}...\n"
                f"**PDF链接**: {result.pdf_url}\n"
                f"**分类**: {', '.join(result.categories)}\n"
                f"**arXiv ID**: {result.entry_id.split('/')[-1]}\n"
            )
            results.append(paper_info)
        
        if results:
            formatted_result = f"找到 {len(results)} 篇相关论文：\n\n" + "\n---\n".join(results)
            logger.info(f"成功获取到 {len(results)} 篇论文")
            return formatted_result
        else:
            return f"未找到关于 '{query}' 的相关论文。"
            
    except Exception as e:
        error_msg = f"arXiv搜索失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


def web_search_function(query: str) -> str:
    """
    Web搜索函数（备用）
    
    Args:
        query: 搜索查询词
    
    Returns:
        str: 搜索结果或提示信息
    """
    try:
        logger.info(f"使用备用Web搜索: {query}")
        
        result = f"""
🔍 关于 "{query}" 的搜索建议：

⚠️ 注意：当前使用的是备用搜索功能。为了获得真实的Web搜索结果，请：

1. **配置Tavily API**:
   - 访问 https://tavily.com/ 注册账户
   - 获取API密钥并添加到.env文件：TAVILY_API_KEY="tvly-your-key"
   - 重新启动应用

2. **建议的研究方向**:
   - 查阅该领域的最新学术论文
   - 关注权威技术博客和官方文档
   - 了解产业应用案例和发展趋势
   - 寻找专家观点和技术报告

3. **手动搜索建议**:
   - Google Scholar: 学术论文搜索
   - arXiv.org: 预印本论文
   - GitHub: 开源项目和代码
   - 技术公司博客: 最新技术动态

🎯 **当前可用功能**: arXiv学术搜索已完全可用，建议重点利用学术论文进行研究。
"""
        
        return result
        
    except Exception as e:
        error_msg = f"Web搜索失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


# 工具定义字典 - CrewAI兼容格式
ARXIV_SEARCH_TOOL = {
    "name": "arxiv_search",
    "description": "在arXiv上搜索学术论文。输入搜索查询词，返回相关论文的详细信息包括标题、作者、摘要、PDF链接等。",
    "function": arxiv_search_function
}

WEB_SEARCH_TOOL = {
    "name": "web_search", 
    "description": "执行Web搜索获取最新信息。当Tavily API不可用时，提供搜索建议和替代方案。",
    "function": web_search_function
}
