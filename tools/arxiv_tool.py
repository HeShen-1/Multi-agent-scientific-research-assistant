"""
arXiv搜索工具
为CrewAI系统提供学术论文搜索功能
"""

import arxiv
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool("ArxivSearchTool")
def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    """
    在arXiv上搜索与给定查询相关的研究论文。
    
    Args:
        query (str): 搜索查询词
        max_results (int): 最大返回结果数量，默认为5
    
    Returns:
        List[Dict]: 包含论文信息的字典列表，每个字典包含：
            - title: 论文标题
            - authors: 作者列表
            - summary: 论文摘要
            - pdf_url: PDF下载链接
            - published_date: 发布日期
            - categories: 论文分类
    """
    try:
        logger.info(f"开始搜索arXiv，查询: {query}")
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate  # 按提交日期排序，获取最新论文
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
                "arxiv_id": result.entry_id.split('/')[-1]  # 提取arXiv ID
            }
            results_list.append(paper_info)
            
        logger.info(f"成功获取到 {len(results_list)} 篇论文")
        return results_list
        
    except Exception as e:
        logger.error(f"arXiv搜索出错: {str(e)}")
        return [{"error": f"搜索失败: {str(e)}"}]


@tool("ArxivDetailedSearchTool")
def search_arxiv_detailed(query: str, max_results: int = 10, category: str = None) -> List[Dict]:
    """
    在arXiv上进行详细搜索，支持更多筛选选项。
    
    Args:
        query (str): 搜索查询词
        max_results (int): 最大返回结果数量，默认为10
        category (str): 可选的论文分类筛选 (如 'cs.AI', 'cs.LG')
    
    Returns:
        List[Dict]: 详细的论文信息列表
    """
    try:
        logger.info(f"开始详细搜索arXiv，查询: {query}, 分类: {category}")
        
        # 如果指定了分类，将其添加到查询中
        search_query = query
        if category:
            search_query = f"cat:{category} AND {query}"
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance  # 按相关性排序
        )
        
        results_list = []
        for result in client.results(search):
            # 计算摘要长度并截取前500字符
            summary = result.summary.strip().replace('\n', ' ')
            if len(summary) > 500:
                summary = summary[:500] + "..."
            
            paper_info = {
                "title": result.title.strip(),
                "authors": [author.name for author in result.authors[:5]],  # 最多显示5个作者
                "summary": summary,
                "pdf_url": result.pdf_url,
                "published_date": result.published.strftime("%Y-%m-%d"),
                "updated_date": result.updated.strftime("%Y-%m-%d") if result.updated else None,
                "categories": result.categories,
                "primary_category": result.primary_category,
                "arxiv_id": result.entry_id.split('/')[-1],
                "comment": result.comment if hasattr(result, 'comment') else None
            }
            results_list.append(paper_info)
            
        logger.info(f"详细搜索成功获取到 {len(results_list)} 篇论文")
        return results_list
        
    except Exception as e:
        logger.error(f"arXiv详细搜索出错: {str(e)}")
        return [{"error": f"详细搜索失败: {str(e)}"}]


def get_arxiv_categories():
    """
    获取arXiv主要分类列表
    
    Returns:
        Dict: arXiv分类信息
    """
    categories = {
        "Computer Science": {
            "cs.AI": "Artificial Intelligence",
            "cs.LG": "Machine Learning", 
            "cs.CV": "Computer Vision and Pattern Recognition",
            "cs.CL": "Computation and Language",
            "cs.NE": "Neural and Evolutionary Computing",
            "cs.RO": "Robotics",
            "cs.SI": "Social and Information Networks"
        },
        "Physics": {
            "physics.optics": "Optics",
            "physics.app-ph": "Applied Physics",
            "cond-mat": "Condensed Matter"
        },
        "Mathematics": {
            "math.ST": "Statistics Theory",
            "math.OC": "Optimization and Control"
        },
        "Quantitative Biology": {
            "q-bio.BM": "Biomolecules",
            "q-bio.GN": "Genomics"
        },
        "Statistics": {
            "stat.ML": "Machine Learning",
            "stat.AP": "Applications"
        }
    }
    return categories
