"""
多智能体科研助手主程序
Multi-Agent Research Assistant Main Program

基于CrewAI的多智能体系统，自动化生成结构化研究报告

使用方法：
    python main.py

作者：AI Assistant
版本：1.0
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
import concurrent.futures

# 导入网络工具
from utils.network_utils import (
    retry_with_backoff, 
    async_retry_with_backoff,
    check_api_connectivity,
    get_optimal_timeout,
    api_rate_limiter
)

# 导入CrewAI核心组件
from crewai import Crew, Process

# 配置DeepSeek API
def setup_deepseek_api():
    """配置DeepSeek API设置"""
    api_base = os.getenv('OPENAI_API_BASE')
    if api_base:
        # 确保API基础URL格式正确
        if not api_base.endswith('/v1') and not api_base.endswith('/'):
            api_base = api_base.rstrip('/') + '/v1'
        os.environ['OPENAI_API_BASE'] = api_base
        logger.info(f"使用DeepSeek API: {api_base}")
    else:
        # 默认使用DeepSeek API
        os.environ['OPENAI_API_BASE'] = "https://api.deepseek.com/v1"
        logger.info("使用默认DeepSeek API端点")
    
    # 设置默认模型
    model_name = os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
    os.environ['OPENAI_MODEL_NAME'] = model_name
    logger.info(f"使用模型: {model_name}")
    
    # 验证API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'sk-your-deepseek-api-key-here':
        logger.error("DeepSeek API密钥未正确设置！")
        logger.error("请在.env文件中设置正确的OPENAI_API_KEY")
        return False
    
    # 检查API连通性（可选，避免启动时阻塞）
    try:
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com/v1')
        if check_api_connectivity(api_base, api_key):
            logger.info("✅ API连通性验证成功")
        else:
            logger.warning("⚠️ API连通性验证失败，但将继续运行")
            logger.warning("如果遇到连接问题，请检查网络和API密钥")
    except Exception as e:
        logger.warning(f"⚠️ API连通性检查跳过: {e}")
    
    return True

# 导入自定义智能体和任务
from agents.research_agents import (
    create_research_manager,
    create_senior_researcher,
    create_research_analyst,
    create_validator_agent
)
from tasks.research_tasks import (
    create_planning_task,
    create_research_execution_task,
    create_analysis_task,
    create_validation_task
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_assistant.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_environment():
    """
    加载环境变量并验证必要的API密钥
    
    Returns:
        bool: 是否成功加载所有必要的环境变量
    """
    # 加载.env文件
    load_dotenv()
    
    # 检查.env文件是否存在
    if not os.path.exists('.env'):
        logger.error("❌ 未找到.env配置文件！")
        logger.error("请按照以下步骤创建配置文件：")
        logger.error("1. 复制 env_example.txt 为 .env")
        logger.error("2. 在 .env 中设置您的 DeepSeek API 密钥")
        logger.error("3. 将 OPENAI_API_KEY 的值替换为您的真实API密钥")
        return False
    
    # 配置DeepSeek API
    if not setup_deepseek_api():
        return False
    
    # 检查可选的Tavily API密钥
    tavily_key = os.getenv('TAVILY_API_KEY')
    if not tavily_key or tavily_key == 'tvly-your-tavily-api-key-here':
        logger.warning("未配置Tavily API密钥，将使用备用搜索功能")
    
    logger.info("✅ 环境变量加载成功")
    return True


def validate_topic(topic: str) -> bool:
    """
    验证研究主题的有效性
    
    Args:
        topic (str): 研究主题
        
    Returns:
        bool: 主题是否有效
    """
    if not topic or len(topic.strip()) < 5:
        logger.error("研究主题过短，请提供更详细的主题描述")
        return False
    
    if len(topic) > 500:
        logger.error("研究主题过长，请简化主题描述")
        return False
    
    return True


def save_report(content: str, topic: str) -> str:
    """
    保存研究报告到文件
    
    Args:
        content (str): 报告内容
        topic (str): 研究主题
        
    Returns:
        str: 保存的文件路径
    """
    # 创建报告目录
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # 生成文件名（使用时间戳避免重复）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_safe = "".join(c for c in topic[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"research_report_{topic_safe}_{timestamp}.md"
    filepath = os.path.join(reports_dir, filename)
    
    # 保存文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"研究报告已保存到: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存报告失败: {str(e)}")
        return ""


def create_research_crew() -> Crew:
    """
    创建多智能体研究团队
    
    Returns:
        Crew: 配置好的CrewAI团队实例
    """
    logger.info("正在创建智能体团队...")
    
    # 创建智能体
    research_manager = create_research_manager()
    senior_researcher = create_senior_researcher()
    research_analyst = create_research_analyst()
    
    logger.info("智能体创建完成")
    
    # 创建Crew（暂时不包含任务，任务将在运行时动态创建）
    # 智能体已经在创建时配置了LLM，这里不需要额外配置
    
    # 创建Crew配置
    crew_config = {
        "agents": [research_manager, senior_researcher, research_analyst],
        "tasks": [],  # 任务将在run_research中动态添加
        "process": Process.sequential,  # 暂时使用顺序流程避免hierarchical的复杂性
        "verbose": True,  # 详细输出模式
        "memory": False,  # 禁用内存以避免embedding API调用
        "max_iter": 3,  # 最大迭代次数
    }
    
    crew = Crew(**crew_config)
    
    logger.info("智能体团队创建完成")
    return crew


def run_research(topic: str) -> str:
    """
    执行完整的研究流程（默认使用并发模式）
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 生成的研究报告内容
    """
    # 默认使用高性能并发模式
    return asyncio.run(run_parallel_research(topic))


def run_research_with_validation(topic: str) -> str:
    """
    执行带验证功能的完整研究流程（推荐用于高质量报告）
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 经过验证的高质量研究报告内容
    """
    return asyncio.run(run_parallel_research_with_validation(topic))


def run_research_sync(topic: str) -> str:
    """
    执行完整的研究流程（传统同步版本）
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 生成的研究报告内容
    """
    logger.info(f"开始同步研究主题: {topic}")
    start_time = datetime.now()
    
    try:
        # 创建智能体团队
        crew = create_research_crew()
        
        # 动态创建任务
        logger.info("创建研究任务...")
        
        # 创建任务并添加到crew中
        planning_task = create_planning_task(crew.agents[0], topic)  # Research Manager
        execution_task = create_research_execution_task(crew.agents[1], topic)  # Senior Researcher
        analysis_task = create_analysis_task(crew.agents[2], topic)  # Research Analyst
        
        # 设置任务依赖关系
        execution_task.context = [planning_task]
        analysis_task.context = [execution_task]
        
        # 将任务添加到crew
        crew.tasks = [planning_task, execution_task, analysis_task]
        
        logger.info("开始执行同步研究流程...")
        
        # 执行研究
        result = crew.kickoff(inputs={"topic": topic})
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"同步研究完成，总耗时: {execution_time:.2f}秒")
        
        # 添加元数据到报告
        metadata = f"""
---
研究主题: {topic}
生成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
执行时间: {execution_time:.2f}秒
执行模式: 传统同步模式
系统版本: Multi-Agent Research Assistant v1.1 (Sync)
---

"""
        
        final_report = metadata + str(result)
        
        # 自动保存到记忆库
        try:
            from tools.memory_tool import get_memory_manager
            memory_manager = get_memory_manager()
            memory_id = memory_manager.store_research(
                topic=topic,
                content=final_report,
                metadata={
                    "execution_mode": "同步模式",
                    "execution_time": f"{execution_time:.2f}秒",
                    "version": "v1.1"
                }
            )
            if memory_id:
                logger.info(f"研究已自动保存到记忆库: {memory_id}")
        except Exception as e:
            logger.warning(f"自动保存记忆失败: {str(e)}")
        
        return final_report
        
    except Exception as e:
        logger.error(f"同步研究过程中发生错误: {str(e)}")
        return f"# 研究报告生成失败\n\n错误信息: {str(e)}\n\n请检查配置和网络连接后重试。"


async def run_research_async(topic: str) -> str:
    """
    执行完整的研究流程（异步版本）
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 生成的研究报告内容
    """
    logger.info(f"开始异步研究主题: {topic}")
    start_time = datetime.now()
    
    try:
        # 创建智能体团队
        crew = create_research_crew()
        
        # 动态创建任务
        logger.info("创建研究任务...")
        
        # 创建任务并添加到crew中
        planning_task = create_planning_task(crew.agents[0], topic)  # Research Manager
        execution_task = create_research_execution_task(crew.agents[1], topic)  # Senior Researcher
        analysis_task = create_analysis_task(crew.agents[2], topic)  # Research Analyst
        
        # 设置任务依赖关系
        execution_task.context = [planning_task]
        analysis_task.context = [execution_task]
        
        # 将任务添加到crew
        crew.tasks = [planning_task, execution_task, analysis_task]
        
        logger.info("开始执行异步研究流程...")
        
        # 使用异步执行研究
        result = await run_crew_async(crew, {"topic": topic})
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"异步研究完成，总耗时: {execution_time:.2f}秒")
        
        # 添加元数据到报告
        metadata = f"""
---
研究主题: {topic}
生成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
执行时间: {execution_time:.2f}秒
执行模式: 异步并发模式
系统版本: Multi-Agent Research Assistant v1.1 (Async)
---

"""
        
        final_report = metadata + str(result)
        
        # 自动保存到记忆库
        try:
            from tools.memory_tool import get_memory_manager
            memory_manager = get_memory_manager()
            memory_id = memory_manager.store_research(
                topic=topic,
                content=final_report,
                metadata={
                    "execution_mode": "异步模式",
                    "execution_time": f"{execution_time:.2f}秒",
                    "version": "v1.1"
                }
            )
            if memory_id:
                logger.info(f"研究已自动保存到记忆库: {memory_id}")
        except Exception as e:
            logger.warning(f"自动保存记忆失败: {str(e)}")
        
        return final_report
        
    except Exception as e:
        logger.error(f"异步研究过程中发生错误: {str(e)}")
        return f"# 研究报告生成失败\n\n错误信息: {str(e)}\n\n请检查配置和网络连接后重试。"


# 移除装饰器，改为内部处理重试
async def run_crew_async(crew: Crew, inputs: Dict[str, Any]) -> str:
    """
    异步运行CrewAI团队（带强化重试机制）
    
    Args:
        crew: CrewAI团队实例
        inputs: 输入参数
        
    Returns:
        str: 执行结果
    """
    max_retries = 5
    base_delay = 2.0
    max_delay = 60.0
    
    for attempt in range(max_retries + 1):
        try:
            # 应用速率限制
            api_rate_limiter.wait_if_needed()
            
            logger.info("开始执行Crew任务...")
            
            # CrewAI 0.28.8+ 支持异步执行
            if hasattr(crew, 'kickoff_async'):
                logger.info("使用CrewAI原生异步执行")
                result = await crew.kickoff_async(inputs=inputs)
            else:
                # 如果不支持原生异步，使用线程池包装
                logger.info("使用线程池包装同步执行")
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        executor, 
                        lambda: crew.kickoff(inputs=inputs)
                    )
            
            logger.info("✅ Crew执行成功")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Crew执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {error_msg}")
            
            # 检查是否是网络相关错误
            network_errors = [
                'connection error', 'timeout', 'cloudflare', 
                'just a moment', 'rate limit', 'too many requests',
                'internal server error', 'bad gateway', 'service unavailable'
            ]
            
            is_network_error = any(error in error_msg.lower() for error in network_errors)
            
            if attempt < max_retries and is_network_error:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.info(f"等待 {delay:.1f} 秒后重试...")
                await asyncio.sleep(delay)
                continue
            else:
                # 非网络错误或已达到最大重试次数
                logger.error(f"所有重试都失败了，最后的错误: {error_msg}")
                raise e


async def run_parallel_research(topic: str) -> str:
    """
    执行并发优化的研究流程
    
    这个版本实现了真正的并行搜索：
    - Web搜索和arXiv搜索同时进行
    - 多个查询并发执行
    - 最大化利用I/O等待时间
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 生成的研究报告内容
    """
    logger.info(f"开始并发研究主题: {topic}")
    start_time = datetime.now()
    
    try:
        # 第一阶段：规划阶段（必须串行）
        planning_crew = create_planning_crew(topic)
        planning_result = await run_crew_async(planning_crew, {"topic": topic})
        
        logger.info("规划阶段完成，开始并发搜索...")
        
        # 第二阶段：并发搜索阶段
        web_search_crew = create_web_search_crew(topic)
        arxiv_search_crew = create_arxiv_search_crew(topic)
        
        # 将 CrewOutput 转换为字符串
        planning_context_str = str(planning_result)
        
        # 并发执行Web搜索和arXiv搜索
        web_task = run_crew_async(web_search_crew, {
            "topic": topic,
            "planning_context": planning_context_str
        })
        arxiv_task = run_crew_async(arxiv_search_crew, {
            "topic": topic, 
            "planning_context": planning_context_str
        })
        
        # 等待所有搜索任务完成
        web_results, arxiv_results = await asyncio.gather(web_task, arxiv_task)
        
        logger.info("并发搜索阶段完成，开始分析...")
        
        # 第三阶段：分析阶段（串行）
        analysis_crew = create_analysis_crew(topic)
        final_result = await run_crew_async(analysis_crew, {
            "topic": topic,
            "web_results": str(web_results),
            "arxiv_results": str(arxiv_results)
        })
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"并发研究完成，总耗时: {execution_time:.2f}秒")
        
        # 添加元数据到报告
        metadata = f"""
---
研究主题: {topic}
生成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
执行时间: {execution_time:.2f}秒
执行模式: 高级并发模式 (Web + arXiv 并行搜索)
系统版本: Multi-Agent Research Assistant v1.1 (Advanced Parallel)
---

"""
        
        final_report = metadata + str(final_result)
        
        # 自动保存到记忆库
        try:
            from tools.memory_tool import get_memory_manager
            memory_manager = get_memory_manager()
            memory_id = memory_manager.store_research(
                topic=topic,
                content=final_report,
                metadata={
                    "execution_mode": "高级并发模式",
                    "execution_time": f"{execution_time:.2f}秒",
                    "version": "v1.1",
                    "parallel_search": True
                }
            )
            if memory_id:
                logger.info(f"研究已自动保存到记忆库: {memory_id}")
        except Exception as e:
            logger.warning(f"自动保存记忆失败: {str(e)}")
        
        return final_report
        
    except Exception as e:
        logger.error(f"并发研究过程中发生错误: {str(e)}")
        return f"# 研究报告生成失败\n\n错误信息: {str(e)}\n\n请检查配置和网络连接后重试。"


def create_planning_crew(topic: str) -> Crew:
    """创建专门用于规划的团队"""
    research_manager = create_research_manager()
    planning_task = create_planning_task(research_manager, topic)
    
    crew = Crew(
        agents=[research_manager],
        tasks=[planning_task],
        process=Process.sequential,
        verbose=True,
        memory=False
    )
    return crew


def create_web_search_crew(topic: str) -> Crew:
    """创建专门用于Web搜索的团队"""
    from tasks.research_tasks import create_web_search_task
    
    web_researcher = create_senior_researcher()
    web_search_task = create_web_search_task(web_researcher, topic)
    
    crew = Crew(
        agents=[web_researcher],
        tasks=[web_search_task],
        process=Process.sequential,
        verbose=True,
        memory=False
    )
    return crew


def create_arxiv_search_crew(topic: str) -> Crew:
    """创建专门用于arXiv搜索的团队"""
    from tasks.research_tasks import create_arxiv_search_task
    
    arxiv_researcher = create_senior_researcher()
    arxiv_search_task = create_arxiv_search_task(arxiv_researcher, topic)
    
    crew = Crew(
        agents=[arxiv_researcher],
        tasks=[arxiv_search_task],
        process=Process.sequential,
        verbose=True,
        memory=False
    )
    return crew


def create_analysis_crew(topic: str) -> Crew:
    """创建专门用于分析的团队"""
    from tasks.research_tasks_fixed import create_integrated_analysis_task_fixed
    
    research_analyst = create_research_analyst()
    analysis_task = create_integrated_analysis_task_fixed(research_analyst, topic)
    
    crew = Crew(
        agents=[research_analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True,
        memory=False
    )
    return crew


def create_validation_crew(topic: str, research_report: str = "") -> Crew:
    """创建专门用于验证的团队"""
    validator = create_validator_agent()
    validation_task = create_validation_task(validator, topic, research_report)
    
    crew = Crew(
        agents=[validator],
        tasks=[validation_task],
        process=Process.sequential,
        verbose=True,
        memory=False
    )
    return crew


async def run_parallel_research_with_validation(topic: str) -> str:
    """
    执行带验证功能的并发研究流程
    
    实现审查循环机制：
    1. 规划阶段（串行）
    2. 并发搜索阶段（Web + arXiv 并行）
    3. 分析阶段（串行）
    4. 验证阶段（串行）
    5. 如果验证不通过，返回分析阶段重新生成报告（最多2次重试）
    
    Args:
        topic (str): 研究主题
        
    Returns:
        str: 经过验证的高质量研究报告内容
    """
    logger.info(f"开始带验证的并发研究主题: {topic}")
    start_time = datetime.now()
    
    try:
        # 第一阶段：规划阶段（必须串行）
        logger.info("阶段1: 研究规划...")
        planning_crew = create_planning_crew(topic)
        planning_result = await run_crew_async(planning_crew, {"topic": topic})
        
        logger.info("规划阶段完成，开始并发搜索...")
        
        # 第二阶段：并发搜索阶段
        logger.info("阶段2: 并发信息搜集...")
        web_search_crew = create_web_search_crew(topic)
        arxiv_search_crew = create_arxiv_search_crew(topic)
        
        # 将 CrewOutput 转换为字符串
        planning_context_str = str(planning_result)
        
        # 并发执行Web搜索和arXiv搜索
        web_task = run_crew_async(web_search_crew, {
            "topic": topic,
            "planning_context": planning_context_str
        })
        arxiv_task = run_crew_async(arxiv_search_crew, {
            "topic": topic, 
            "planning_context": planning_context_str
        })
        
        # 等待所有搜索任务完成
        web_results, arxiv_results = await asyncio.gather(web_task, arxiv_task)
        
        logger.info("并发搜索阶段完成，开始分析和验证循环...")
        
        # 第三阶段：分析和验证循环（最多3次尝试）
        max_validation_attempts = 3
        validation_passed = False
        final_report = None
        validation_feedback = ""
        
        for attempt in range(max_validation_attempts):
            logger.info(f"阶段3.{attempt+1}: 分析阶段（尝试 {attempt+1}/{max_validation_attempts}）...")
            
            # 分析阶段 - 使用修复版本的函数
            from tasks.research_tasks_fixed import create_integrated_analysis_task_fixed
            research_analyst = create_research_analyst()
            
            # 根据是否有验证反馈创建不同的任务
            if attempt > 0:
                analysis_task = create_integrated_analysis_task_fixed(research_analyst, topic, validation_feedback)
                logger.info(f"基于验证反馈进行报告改进...")
            else:
                analysis_task = create_integrated_analysis_task_fixed(research_analyst, topic)
            
            analysis_crew = Crew(
                agents=[research_analyst],
                tasks=[analysis_task],
                process=Process.sequential,
                verbose=True,
                memory=False
            )
            
            analysis_inputs = {
                "topic": topic,
                "web_results": str(web_results),
                "arxiv_results": str(arxiv_results)
            }
            
            analysis_result = await run_crew_async(analysis_crew, analysis_inputs)
            
            logger.info(f"阶段4.{attempt+1}: 验证阶段（尝试 {attempt+1}/{max_validation_attempts}）...")
            
            # 验证阶段
            validation_crew = create_validation_crew(topic, str(analysis_result))
            validation_result = await run_crew_async(validation_crew, {
                "topic": topic,
                "research_report": str(analysis_result)
            })
            
            # 解析验证结果
            validation_result_str = str(validation_result)
            
            # 简单的验证结果解析（实际项目中可以更复杂）
            if "验证通过" in validation_result_str or "质量评级：优秀" in validation_result_str or "质量评级：良好" in validation_result_str:
                validation_passed = True
                final_report = str(analysis_result)
                logger.info(f"✅ 验证通过！（尝试 {attempt+1}/{max_validation_attempts}）")
                break
            else:
                logger.info(f"⚠️ 验证未通过（尝试 {attempt+1}/{max_validation_attempts}），准备改进...")
                validation_feedback = validation_result_str
                if attempt == max_validation_attempts - 1:
                    # 最后一次尝试，即使验证未通过也使用最后的报告
                    final_report = str(analysis_result)
                    logger.warning("已达到最大验证尝试次数，使用最终版本报告")
        
        if not final_report:
            raise Exception("报告生成失败")
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"带验证的并发研究完成，总耗时: {execution_time:.2f}秒")
        
        # 添加元数据到报告
        validation_status = "✅ 验证通过" if validation_passed else "⚠️ 部分验证"
        metadata = f"""
---
研究主题: {topic}
生成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
执行时间: {execution_time:.2f}秒
执行模式: 高级并发模式 + 质量验证循环
验证状态: {validation_status}
系统版本: Multi-Agent Research Assistant v1.2 (Advanced Parallel + Validation)
---

"""
        
        final_report_with_metadata = metadata + final_report
        
        # 自动保存到记忆库
        try:
            from tools.memory_tool import get_memory_manager
            memory_manager = get_memory_manager()
            memory_id = memory_manager.store_research(
                topic=topic,
                content=final_report_with_metadata,
                metadata={
                    "execution_mode": "高级并发模式+验证",
                    "execution_time": f"{execution_time:.2f}秒",
                    "version": "v1.2",
                    "parallel_search": True,
                    "validation_enabled": True,
                    "validation_passed": validation_passed
                }
            )
            if memory_id:
                logger.info(f"研究已自动保存到记忆库: {memory_id}")
        except Exception as e:
            logger.warning(f"自动保存记忆失败: {str(e)}")
        
        return final_report_with_metadata
        
    except Exception as e:
        logger.error(f"带验证的并发研究过程中发生错误: {str(e)}")
        return f"# 研究报告生成失败\n\n错误信息: {str(e)}\n\n请检查配置和网络连接后重试。"


def interactive_mode():
    """
    交互模式，允许用户输入研究主题
    """
    print("\n" + "="*60)
    print("🤖 多智能体科研助手 (Multi-Agent Research Assistant)")
    print("="*60)
    print("这是一个基于CrewAI的智能研究系统，可以自动生成结构化研究报告。")
    print("输入 'quit' 或 'exit' 退出程序。")
    print("="*60 + "\n")
    
    while True:
        try:
            # 获取用户输入
            topic = input("📝 请输入您想要研究的主题: ").strip()
            
            # 检查退出命令
            if topic.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用多智能体科研助手！")
                break
            
            # 验证主题
            if not validate_topic(topic):
                continue
            
            print(f"\n🚀 开始研究主题: {topic}")
            
            # 询问执行模式
            mode_choice = input("🔧 选择执行模式 [1-标准模式, 2-异步模式, 3-并发模式, 4-验证模式] (默认:4): ").strip()
            if mode_choice == "1":
                print("⏳ 使用标准同步模式，智能体团队正在工作中...")
                result = run_research_sync(topic)
            elif mode_choice == "2":
                print("⚡ 使用异步模式，智能体团队正在高效工作中...")
                result = asyncio.run(run_research_async(topic))
            elif mode_choice == "3":
                print("🚀 使用高级并发模式，最大化性能...")
                result = asyncio.run(run_parallel_research(topic))
            else:
                print("🔍 使用验证模式，确保最高质量报告...")
                result = asyncio.run(run_parallel_research_with_validation(topic))
            
            # 保存报告
            filepath = save_report(result, topic)
            
            # 显示结果摘要
            print("\n" + "="*60)
            print("✅ 研究完成！")
            if filepath:
                print(f"📄 报告已保存到: {filepath}")
            print("="*60)
            
            # 询问是否查看报告摘要
            show_summary = input("\n📖 是否显示报告摘要？(y/n): ").strip().lower()
            if show_summary in ['y', 'yes', 'Y', '是']:
                # 显示报告的前500字符
                print("\n📋 报告摘要:")
                print("-" * 40)
                print(result[:500] + "..." if len(result) > 500 else result)
                print("-" * 40)
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 程序已中断，感谢使用！")
            break
        except Exception as e:
            logger.error(f"交互模式发生错误: {str(e)}")
            print(f"❌ 发生错误: {str(e)}")


def main():
    """
    主函数
    """
    try:
        # 检查环境变量
        if not load_environment():
            sys.exit(1)
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            # 命令行模式
            topic = " ".join(sys.argv[1:])
            if validate_topic(topic):
                result = run_research(topic)
                filepath = save_report(result, topic)
                print(f"研究完成，报告已保存到: {filepath}")
            else:
                print("无效的研究主题")
                sys.exit(1)
        else:
            # 交互模式
            interactive_mode()
            
    except Exception as e:
        logger.error(f"程序运行发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
