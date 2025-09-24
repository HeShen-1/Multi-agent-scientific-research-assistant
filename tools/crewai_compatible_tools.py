"""
CrewAI兼容的工具定义
解决不同版本CrewAI的工具兼容性问题
"""

import arxiv
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 尝试导入CrewAI工具基类
try:
    from crewai_tools import BaseTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    # 如果不可用，创建一个基础类
    class BaseTool:
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
            
        def _run(self, *args, **kwargs):
            raise NotImplementedError
    
    CREWAI_TOOLS_AVAILABLE = False


class ArxivSearchTool(BaseTool):
    """ArXiv搜索工具 - CrewAI兼容版本"""
    
    def __init__(self):
        super().__init__(
            name="ArxivSearchTool",
            description="在arXiv上搜索与给定查询相关的研究论文，返回论文标题、作者、摘要、PDF链接和发布日期。"
        )
    
    def _run(self, query: str, max_results: int = 5) -> List[Dict]:
        """执行arXiv搜索"""
        try:
            logger.info(f"开始搜索arXiv，查询: {query}")
            
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            results_list = []
            for result in client.results(search):
                paper_info = {
                    "title": result.title.strip(),
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary.strip().replace('\n', ' '),
                    "pdf_url": result.pdf_url,
                    "published_date": result.published.strftime("%Y-%m-%d"),
                    "categories": result.categories,
                    "arxiv_id": result.entry_id.split('/')[-1]
                }
                results_list.append(paper_info)
                
            logger.info(f"成功获取到 {len(results_list)} 篇论文")
            return results_list
            
        except Exception as e:
            logger.error(f"arXiv搜索出错: {str(e)}")
            return [{"error": f"搜索失败: {str(e)}"}]


class WebSearchTool(BaseTool):
    """Web搜索工具 - CrewAI兼容版本"""
    
    def __init__(self):
        super().__init__(
            name="WebSearchTool", 
            description="执行Web搜索，返回相关的搜索结果。当Tavily不可用时提供备用搜索功能。"
        )
    
    def _run(self, query: str) -> str:
        """执行Web搜索"""
        try:
            logger.info(f"使用备用Web搜索: {query}")
            
            result = f"""
基于查询 "{query}" 的搜索结果：

注意：当前使用的是备用搜索工具。为了获得真实的Web搜索结果，请：
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
            logger.error(f"Web搜索失败: {str(e)}")
            return f"搜索失败: {str(e)}"


# 创建工具实例
def get_arxiv_tool():
    """获取arXiv搜索工具实例"""
    return ArxivSearchTool()


def get_web_search_tool():
    """获取Web搜索工具实例"""
    return WebSearchTool()


# 备用的简单函数工具
def simple_arxiv_search(query: str, max_results: int = 5) -> str:
    """简单的arXiv搜索函数"""
    tool = ArxivSearchTool()
    results = tool._run(query, max_results)
    
    if not results or (len(results) == 1 and "error" in results[0]):
        return f"arXiv搜索失败: {results[0].get('error', '未知错误') if results else '无结果'}"
    
    # 格式化结果
    formatted_results = []
    for paper in results:
        formatted_results.append(
            f"标题: {paper['title']}\n"
            f"作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}\n"
            f"发布日期: {paper['published_date']}\n"
            f"摘要: {paper['summary'][:200]}...\n"
            f"链接: {paper['pdf_url']}\n"
            f"分类: {', '.join(paper['categories'])}\n"
        )
    
    return "\n" + "="*50 + "\n".join(formatted_results)


def simple_web_search(query: str) -> str:
    """简单的Web搜索函数"""
    tool = WebSearchTool()
    return tool._run(query)
