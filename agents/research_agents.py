"""
多智能体科研助手的智能体定义
定义Research Manager、Senior Researcher、Research Analyst三个核心智能体
"""

from crewai import Agent
from tools.simple_tools import arxiv_search_function, web_search_function
import os
from dotenv import load_dotenv

# 尝试导入Tavily搜索工具，如果失败则使用备用方案
try:
    from crewai_tools import TavilySearchResults
    TAVILY_AVAILABLE = True
except ImportError:
    try:
        from crewai_tools import TavilySearchTool as TavilySearchResults
        TAVILY_AVAILABLE = True
    except ImportError:
        # 如果都无法导入，我们将使用备用搜索工具
        TAVILY_AVAILABLE = False
        print("⚠️ Tavily搜索工具未找到，将使用备用Web搜索功能")


def create_research_manager() -> Agent:
    """
    创建研究经理智能体（带记忆功能）
    
    Returns:
        Agent: Research Manager智能体实例
    """
    # 暂时禁用记忆工具以避免兼容性问题
    # CrewAI对工具格式有严格要求，记忆工具需要重构
    memory_tools = []
    print("ℹ️ 记忆工具暂时禁用以确保兼容性")
    
    return Agent(
        role='Research Manager',
        goal='制定全面的研究计划，将复杂的研究主题分解为具体的、可执行的搜索任务，并监督整个研究过程确保质量。利用历史研究记忆避免重复工作并建立在已有基础上。',
        backstory="""你是一位经验丰富的实验室主任，拥有多年的科研管理经验和卓越的记忆管理能力。你擅长：
        - 快速理解复杂的研究主题和用户需求
        - 查询和利用历史研究知识，避免重复劳动
        - 将宏大的研究方向分解为具体可操作的子任务
        - 制定高效的搜索策略，平衡广度和深度
        - 协调团队成员，确保研究的全面性和系统性
        - 把控研究质量，确保最终报告的专业性和准确性
        - 善于发现相关历史研究之间的关联和互补性
        
        你总是站在战略高度思考问题，能够预见潜在的研究盲点，并制定相应的补充计划。
        你的工作流程始终包括：1)回忆相关历史研究 2)基于历史知识制定新的研究计划 3)识别知识空白和需要更新的领域。
        
        注意：如果记忆工具不可用，请按常规流程制定研究计划。""",
        tools=memory_tools,  # 添加记忆工具（如果可用）
        verbose=True,
        allow_delegation=True,  # 允许委派任务给其他智能体
        memory=True,  # 启用记忆功能
        max_iter=3,  # 最大迭代次数
        max_execution_time=300,  # 最大执行时间（秒）
        llm=create_crewai_compatible_llm()  # 使用兼容的LLM实例
    )


def create_senior_researcher() -> Agent:
    """
    创建高级研究员智能体
    
    Returns:
        Agent: Senior Researcher智能体实例
    """
    # 初始化搜索工具 - 使用简化配置避免验证问题
    tools = []
    
    # 添加Web搜索工具
    if TAVILY_AVAILABLE:
        try:
            tavily_tool = TavilySearchResults(max_results=5)
            tools.append(tavily_tool)
            print("✅ Tavily搜索工具已启用")
        except Exception as e:
            print(f"⚠️ Tavily工具初始化失败: {e}")
            print("继续使用基础搜索功能")
    
    # 注意: 暂时移除自定义工具以避免验证问题
    # 智能体将依赖LLM的内置知识和Tavily搜索（如果可用）
    
    return Agent(
        role='Senior Researcher',
        goal='根据Research Manager的指导，高效地从互联网和学术数据库中搜集最新、最相关、最权威的研究信息。',
        backstory="""你是一位顶尖的信息学专家，具有以下特长：
        - 精通各种搜索引擎和学术数据库的高级搜索技巧
        - 能够快速识别信息的权威性和可靠性
        - 擅长使用布尔逻辑和关键词组合来精确定位目标信息
        - 对学术文献的结构和引用关系有深刻理解
        - 始终追求信息的时效性，优先关注最新的研究进展
        
        你像一个不知疲倦的信息侦探，总能在海量数据中找到最有价值的内容。你的搜索结果总是准确、全面且组织良好。""",
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=5,
        max_execution_time=600,
        llm=create_crewai_compatible_llm()  # 使用兼容的LLM实例
    )


def create_research_analyst() -> Agent:
    """
    创建研究分析师智能体
    
    Returns:
        Agent: Research Analyst智能体实例
    """
    return Agent(
        role='Research Analyst',
        goal='深度分析搜集到的信息，撰写结构清晰、洞察深刻、引用准确的高质量研究报告。',
        backstory="""你是一位为国际顶级期刊撰稿的资深科学作家，具备以下核心能力：
        - 卓越的信息整合和分析能力，能从零散信息中提炼核心洞见
        - 强大的批判性思维，能够客观评估不同观点和证据
        - 优秀的学术写作技巧，擅长创建逻辑清晰的论述结构
        - 深刻的跨学科理解，能够发现不同领域间的关联
        - 严谨的引用和事实核查习惯，确保信息准确性
        
        你的报告以其深度分析、独到见解和清晰表达而闻名。你总能将复杂的技术概念转化为引人入胜且易于理解的叙述。""",
        verbose=True,
        memory=True,
        max_iter=3,
        max_execution_time=600,
        llm=create_crewai_compatible_llm()  # 使用兼容的LLM实例
    )


def create_validator_agent() -> Agent:
    """
    创建验证智能体（用于未来的质量控制功能）
    
    Returns:
        Agent: Validator智能体实例
    """
    tools = []
    
    # 添加Web搜索工具（如果可用）  
    if TAVILY_AVAILABLE:
        try:
            tavily_tool = TavilySearchResults(max_results=3)
            tools.append(tavily_tool)
            print("✅ Validator的Tavily搜索工具已启用")
        except Exception as e:
            print(f"⚠️ Validator的Tavily工具初始化失败: {e}")
    
    # 注意: 暂时移除自定义工具以避免验证问题
    # Validator将依赖LLM的内置知识进行验证
    
    return Agent(
        role='Research Validator',
        goal='验证研究报告中关键声明和引用的准确性，确保信息的可靠性和完整性。',
        backstory="""你是一名一丝不苟的事实核查专家，以下是你的专业特长：
        - 对任何未经验证的声明都保持健康的怀疑态度
        - 精通交叉验证技巧，能够从多个独立来源确认信息
        - 敏锐地发现逻辑漏洞和潜在的偏见
        - 严格按照学术标准检查引用格式和链接有效性
        - 具备识别伪科学和误导信息的专业能力
        
        你的使命是确保每一份发布的报告都经得起严格的学术审查，无懈可击。""",
        tools=tools,
        verbose=True,
        memory=True,
        max_iter=2,
        max_execution_time=300,
        llm=create_crewai_compatible_llm()  # 使用兼容的LLM实例
    )


# 获取模型配置
def get_model_config():
    """获取OpenAI客户端配置"""
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com')
    model_name = os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY 环境变量未设置。请设置DeepSeek API密钥。")
    
    # 修复常见的错误URL
    if 'www.deepseek.com' in api_base:
        api_base = 'https://api.deepseek.com'
    
    # 确保base_url格式正确（不包含/v1，OpenAI SDK会自动添加）
    if api_base.endswith('/v1'):
        api_base = api_base[:-3]
    
    return {
        'api_key': api_key,
        'base_url': api_base,
        'model': model_name
    }


def create_openai_client():
    """创建OpenAI客户端实例"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI SDK未安装，请运行: pip install openai")
    
    config = get_model_config()
    
    try:
        client = OpenAI(
            api_key=config['api_key'],
            base_url=config['base_url']
        )
        return client
    except Exception as e:
        print(f"⚠️ OpenAI客户端创建失败: {e}")
        raise


def get_model_name():
    """获取模型名称（保持向后兼容性）"""
    try:
        config = get_model_config()
        return config['model']
    except Exception as e:
        print(f"⚠️ 获取模型配置失败: {e}")
        return 'deepseek-chat'


def create_crewai_compatible_llm():
    """创建与CrewAI兼容的LLM实例"""
    try:
        # 首先尝试使用langchain_openai（CrewAI的首选方式）
        from langchain_openai import ChatOpenAI
        
        config = get_model_config()
        
        # 尝试多种配置方法来解决LiteLLM兼容性问题
        
        # 方法1: 使用openai/格式（通用OpenAI兼容API）
        try:
            llm = ChatOpenAI(
                model=f"openai/{config['model']}",  # 使用openai前缀
                openai_api_key=config['api_key'],
                openai_api_base=config['base_url'] + '/v1',
                temperature=0.7,
                max_tokens=4000,
                timeout=60
            )
            print(f"✅ 使用openai前缀创建LLM实例，模型: openai/{config['model']}")
            return llm
        except Exception as e1:
            print(f"⚠️ openai前缀方法失败: {e1}")
            
            # 方法2: 直接使用模型名称，设置自定义LLM提供商
            try:
                llm = ChatOpenAI(
                    model=config['model'],
                    openai_api_key=config['api_key'],
                    openai_api_base=config['base_url'] + '/v1',
                    temperature=0.7,
                    max_tokens=4000,
                    timeout=60,
                    model_kwargs={
                        "custom_llm_provider": "openai"  # 强制使用OpenAI兼容格式
                    }
                )
                print(f"✅ 使用自定义提供商创建LLM实例，模型: {config['model']}")
                return llm
            except Exception as e2:
                print(f"⚠️ 自定义提供商方法失败: {e2}")
                
                # 方法3: 使用deepseek前缀（原方法）
                try:
                    llm = ChatOpenAI(
                        model=f"deepseek/{config['model']}",
                        openai_api_key=config['api_key'],
                        openai_api_base=config['base_url'] + '/v1',
                        temperature=0.7,
                        max_tokens=4000,
                        timeout=60
                    )
                    print(f"✅ 使用deepseek前缀创建LLM实例，模型: deepseek/{config['model']}")
                    return llm
                except Exception as e3:
                    print(f"⚠️ deepseek前缀方法也失败: {e3}")
                    raise e3
        
    except ImportError:
        print("⚠️ langchain_openai不可用，尝试使用模型名称")
        return get_model_name()
    except Exception as e:
        print(f"⚠️ 所有LLM创建方法都失败: {e}")
        return get_model_name()


def test_openai_client():
    """测试OpenAI客户端连接（可选的测试函数）"""
    try:
        client = create_openai_client()
        config = get_model_config()
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello, please respond with 'Connection successful!'"},
            ],
            stream=False,
            max_tokens=50
        )
        
        print(f"✅ OpenAI客户端测试成功: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI客户端测试失败: {e}")
        return False

# 智能体配置字典，便于管理
AGENT_CONFIGS = {
    'research_manager': {
        'temperature': 0.7,
        'model': get_model_name(),
        'llm_factory': create_crewai_compatible_llm
    },
    'senior_researcher': {
        'temperature': 0.5,  # 更低的温度确保搜索的一致性
        'model': get_model_name(),
        'llm_factory': create_crewai_compatible_llm
    },
    'research_analyst': {
        'temperature': 0.8,  # 更高的温度鼓励创造性分析
        'model': get_model_name(),
        'llm_factory': create_crewai_compatible_llm
    },
    'validator': {
        'temperature': 0.3,  # 最低温度确保严格验证
        'model': get_model_name(),
        'llm_factory': create_crewai_compatible_llm
    }
}
