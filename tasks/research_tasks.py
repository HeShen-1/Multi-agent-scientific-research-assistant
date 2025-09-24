"""
多智能体科研助手的任务定义
定义研究流程中的各个任务，包括规划、执行和分析阶段
"""

from crewai import Task
from agents.research_agents import (
    create_research_manager,
    create_senior_researcher, 
    create_research_analyst,
    create_validator_agent
)


def create_planning_task(research_manager, topic: str) -> Task:
    """
    创建研究规划任务（支持历史记忆）
    
    Args:
        research_manager: Research Manager智能体实例
        topic: 研究主题
        
    Returns:
        Task: 规划任务实例
    """
    return Task(
        description=f"""
        作为Research Manager，你需要为主题 '{topic}' 制定一个全面的研究计划。
        
        **首先，利用你的记忆功能回忆过去的相关研究：**
        1. 使用 recall_past_research 工具搜索与当前主题相关的历史研究
        2. 分析历史研究的覆盖范围、时效性和知识空白
        3. 识别可以建立在已有基础上的研究方向
        4. 确定需要更新或补充的知识领域
        
        **然后，基于历史知识制定新的研究计划：**
        1. 分析研究主题的核心要素和关键概念
        2. 识别需要深入探索的子领域和相关技术（避免与历史研究重复）
        3. 制定搜索策略，包括：
           - 用于Tavily通用Web搜索的查询列表（至少3-5个查询，重点关注最新进展）
           - 用于arXiv学术搜索的查询列表（至少2-4个查询，关注近期论文）
        4. 确定研究的时间范围和优先级（基于历史研究的时间线）
        5. 预期可能遇到的挑战和解决方案
        
        **搜索查询应该：**
        - 覆盖历史研究未涉及或需要更新的方面
        - 包含最新技术术语和相关概念
        - 考虑实际应用场景和产业趋势的最新变化
        - 平衡技术深度和应用广度
        - 关注时效性，优先搜索近期（2023-2024年）的信息
        
        **如果没有找到相关历史研究，则按常规流程制定全面的研究计划。**
        """,
        agent=research_manager,
        expected_output="""
        一个详细的研究计划，包含：
        1. 主题分析摘要
        2. 核心研究方向列表
        3. Web搜索查询列表（JSON格式）
        4. arXiv搜索查询列表（JSON格式）
        5. 研究优先级和预期产出
        
        格式示例：
        ## 研究计划
        
        ### 主题分析
        [主题的核心要素分析]
        
        ### Web搜索查询
        ```json
        {
            "web_queries": [
                "query1: 具体搜索词",
                "query2: 具体搜索词",
                ...
            ]
        }
        ```
        
        ### arXiv搜索查询  
        ```json
        {
            "arxiv_queries": [
                "query1: 学术搜索词",
                "query2: 学术搜索词", 
                ...
            ]
        }
        ```
        """
    )


def create_research_execution_task(senior_researcher, topic: str) -> Task:
    """
    创建研究执行任务
    
    Args:
        senior_researcher: Senior Researcher智能体实例
        topic: 研究主题
        
    Returns:
        Task: 执行任务实例
    """
    return Task(
        description=f"""
        根据Research Manager制定的研究计划，执行全面的信息搜集任务。
        
        你需要：
        1. 仔细分析Research Manager提供的搜索查询列表
        2. 使用TavilySearchResults工具执行所有Web搜索查询
        3. 使用ArxivSearchTool执行所有学术论文搜索
        4. 对每个搜索结果进行初步评估和筛选
        5. 整理和结构化所有搜集到的信息
        
        搜索要求：
        - 每个Web查询搜索最相关的5个结果
        - 每个arXiv查询搜索最新的5-10篇论文
        - 优先选择权威来源和最新信息
        - 记录每个信息来源的详细引用信息
        
        主题：{topic}
        """,
        agent=senior_researcher,
        expected_output="""
        一份完整的信息搜集报告，包含：
        
        ## Web搜索结果
        ### 查询1：[查询内容]
        - 来源1：[标题] - [URL] - [关键要点]
        - 来源2：[标题] - [URL] - [关键要点]
        ...
        
        ### 查询2：[查询内容]
        ...
        
        ## 学术论文搜索结果
        ### arXiv查询1：[查询内容]
        - 论文1：[标题] - 作者 - [发布日期] - [arXiv ID] - [摘要关键点]
        - 论文2：[标题] - 作者 - [发布日期] - [arXiv ID] - [摘要关键点]
        ...
        
        ### arXiv查询2：[查询内容]
        ...
        
        ## 搜集总结
        - 总共搜集的Web来源数量：X个
        - 总共搜集的学术论文数量：Y篇
        - 信息覆盖的时间范围：从X年到Y年
        - 发现的主要技术趋势和热点
        """
    )


def create_analysis_task(research_analyst, topic: str) -> Task:
    """
    创建分析和报告撰写任务
    
    Args:
        research_analyst: Research Analyst智能体实例
        topic: 研究主题
        
    Returns:
        Task: 分析任务实例
    """
    return Task(
        description=f"""
        基于Senior Researcher搜集的所有信息，撰写一份全面、深刻、结构化的研究报告。
        
        分析要求：
        1. 深度阅读和理解所有搜集到的信息
        2. 识别关键技术趋势和突破性进展
        3. 进行批判性分析和不同观点的对比
        4. 提供独到的见解和前瞻性判断
        5. 确保所有引用来源准确标注
        
        报告结构：
        1. 执行摘要（Executive Summary）
        2. 引言和背景（Introduction & Background）  
        3. 核心技术发现（Key Technical Findings）
        4. 深度分析（In-depth Analysis）
        5. 趋势预测（Future Trends）
        6. 结论和建议（Conclusions & Recommendations）
        7. 参考文献（References）
        
        写作要求：
        - 使用学术化但易读的语言
        - 逻辑清晰，论证有力
        - 包含具体的技术细节和数据
        - 所有引用使用Markdown链接格式
        - 总字数不少于1500字
        
        主题：{topic}
        """,
        agent=research_analyst,
        expected_output="""
        一份完整的Markdown格式研究报告，包含以下结构：
        
        # [报告标题]
        
        ## 执行摘要
        [3-5句话概括核心发现和结论]
        
        ## 1. 引言和背景
        [介绍研究主题的重要性和背景]
        
        ## 2. 核心技术发现
        ### 2.1 [子主题1]
        [具体技术内容和发现]
        
        ### 2.2 [子主题2]
        [具体技术内容和发现]
        
        ## 3. 深度分析
        ### 3.1 技术对比分析
        [不同技术方案的对比]
        
        ### 3.2 优势与挑战
        [客观分析优势和面临的挑战]
        
        ## 4. 趋势预测
        [基于当前发现的未来发展趋势预测]
        
        ## 5. 结论和建议
        [总结性结论和实用建议]
        
        ## 6. 参考文献
        - [来源1标题](URL) - 访问日期
        - [来源2标题](URL) - 访问日期
        - [论文1] Author et al. - arXiv:XXXX.XXXXX
        ...
        """
    )


def create_validation_task(validator, topic: str, research_report: str = "") -> Task:
    """
    创建验证任务（可选，用于质量控制）
    
    Args:
        validator: Validator智能体实例
        topic: 研究主题
        
    Returns:
        Task: 验证任务实例
    """
    return Task(
        description=f"""
        对Research Analyst生成的研究报告进行严格的质量验证。
        
        验证要求：
        1. 事实准确性检查
           - 随机选择3-5个关键技术声明进行交叉验证
           - 验证重要数据和统计信息的准确性
           
        2. 引用来源验证
           - 检查所有链接的有效性
           - 验证引用信息的准确性和完整性
           
        3. 逻辑一致性检查
           - 检查论述逻辑是否严密
           - 识别可能的偏见或片面观点
           
        4. 技术内容审查
           - 评估技术描述的准确性
           - 检查是否存在过时或错误信息
        
        主题：{topic}
        研究报告：{research_report}
        """,
        agent=validator,
        expected_output="""
        验证报告格式：
        
        ## 验证结果总结
        - 整体质量评级：[优秀/良好/需要改进]
        - 主要问题数量：X个
        - 验证通过率：X%
        
        ## 详细验证结果
        
        ### 1. 事实准确性验证
        #### 验证项目1：[声明内容]
        - 验证结果：[通过/有问题]
        - 详细说明：[具体说明]
        
        ### 2. 引用来源验证
        - 有效链接数量：X个
        - 无效链接数量：Y个
        - 需要修正的引用：[列表]
        
        ### 3. 发现的问题和建议
        - 问题1：[描述]
        - 建议1：[具体建议]
        
        ### 4. 最终建议
        [总体建议和改进方向]
        """
    )


# 新增：专门用于并发执行的任务函数

def create_web_search_task(web_researcher, topic: str) -> Task:
    """
    创建专门的Web搜索任务（用于并发执行）
    
    Args:
        web_researcher: Web搜索专用智能体实例
        topic: 研究主题
        
    Returns:
        Task: Web搜索任务实例
    """
    return Task(
        description="""
        专门执行Web搜索任务，基于规划阶段的指导进行高效的网络信息搜集。
        
        你需要：
        1. 分析规划阶段提供的Web搜索查询列表（来自planning_context）
        2. 使用TavilySearchResults工具执行所有Web搜索查询
        3. 对每个搜索结果进行质量评估和相关性筛选
        4. 优先选择权威来源、最新信息和高质量内容
        5. 整理并结构化所有Web搜索信息
        
        搜索优化要求：
        - 每个查询搜索5-8个最相关结果
        - 重点关注权威媒体、技术博客、官方文档
        - 记录详细的来源信息和访问时间
        - 提取关键信息点和核心观点
        
        研究主题：{topic}
        规划上下文：{planning_context}
        """,
        agent=web_researcher,
        expected_output="""
        完整的Web搜索结果报告，格式如下：
        
        ## Web搜索执行报告
        
        ### 搜索查询执行情况
        - 总查询数量：X个
        - 成功执行：Y个
        - 总结果数量：Z个
        
        ### 详细搜索结果
        
        #### 查询1：[具体查询内容]
        **搜索结果：**
        1. **[标题]** - [来源] - [日期]
           - URL: [链接]
           - 关键要点: [核心信息摘要]
           - 权威性评级: ⭐⭐⭐⭐⭐
        
        2. **[标题]** - [来源] - [日期]
           - URL: [链接]
           - 关键要点: [核心信息摘要]
           - 权威性评级: ⭐⭐⭐⭐⭐
        
        #### 查询2：[具体查询内容]
        ...
        
        ### Web搜索洞察总结
        - 发现的主要趋势：[趋势分析]
        - 关键技术热点：[技术要点]
        - 信息时效性：从[开始时间]到[结束时间]
        - 权威来源占比：X%
        """
    )


def create_arxiv_search_task(arxiv_researcher, topic: str) -> Task:
    """
    创建专门的arXiv搜索任务（用于并发执行）
    
    Args:
        arxiv_researcher: arXiv搜索专用智能体实例
        topic: 研究主题
        
    Returns:
        Task: arXiv搜索任务实例
    """
    return Task(
        description="""
        专门执行arXiv学术论文搜索任务，基于规划阶段的指导进行深度学术文献搜集。
        
        你需要：
        1. 分析规划阶段提供的arXiv搜索查询列表（来自planning_context）
        2. 使用ArxivSearchTool执行所有学术搜索查询
        3. 对每篇论文进行学术价值和相关性评估
        4. 优先选择最新发表、高引用、权威作者的论文
        5. 提取和整理所有关键学术信息
        
        学术搜索要求：
        - 每个查询搜索8-12篇最相关论文
        - 优先考虑近2年的最新研究
        - 关注顶级会议和期刊的论文
        - 记录完整的论文元数据和引用信息
        - 提取摘要中的核心贡献和创新点
        
        研究主题：{topic}
        规划上下文：{planning_context}
        """,
        agent=arxiv_researcher,
        expected_output="""
        完整的arXiv搜索结果报告，格式如下：
        
        ## arXiv学术搜索执行报告
        
        ### 搜索查询执行情况
        - 总查询数量：X个
        - 成功执行：Y个
        - 总论文数量：Z篇
        
        ### 详细搜索结果
        
        #### 学术查询1：[具体查询内容]
        **搜索结果：**
        1. **[论文标题]**
           - 作者: [作者列表]
           - 发布日期: [YYYY-MM-DD]
           - arXiv ID: [arXiv:XXXX.XXXXX]
           - PDF链接: [链接]
           - 核心贡献: [主要创新点和贡献]
           - 技术关键词: [关键技术术语]
           - 学术价值: ⭐⭐⭐⭐⭐
        
        2. **[论文标题]**
           - 作者: [作者列表]
           - 发布日期: [YYYY-MM-DD]
           - arXiv ID: [arXiv:XXXX.XXXXX]
           - PDF链接: [链接]
           - 核心贡献: [主要创新点和贡献]
           - 技术关键词: [关键技术术语]
           - 学术价值: ⭐⭐⭐⭐⭐
        
        #### 学术查询2：[具体查询内容]
        ...
        
        ### arXiv搜索洞察总结
        - 学术研究趋势：[当前研究方向和热点]
        - 技术演进路径：[技术发展脉络]
        - 研究活跃度：[发表频率和研究热度]
        - 权威研究团队：[主要研究机构和学者]
        - 时间分布：从[最早论文日期]到[最新论文日期]
        """
    )


def create_integrated_analysis_task(research_analyst, topic: str, validation_feedback: str = "") -> Task:
    """
    创建整合分析任务（专门处理并发搜索的结果）
    
    Args:
        research_analyst: Research Analyst智能体实例
        topic: 研究主题
        
    Returns:
        Task: 整合分析任务实例
    """
    return Task(
        description="""
        基于并发执行的Web搜索和arXiv搜索结果，进行深度整合分析并撰写高质量研究报告。
        
        整合分析要求：
        1. 深度阅读和理解来自两个搜索渠道的所有信息
        2. 识别Web信息和学术论文之间的关联和互补
        3. 进行跨来源的交叉验证和一致性检查
        4. 整合产业视角（Web信息）和学术视角（arXiv论文）
        5. 提供全面、平衡、深刻的分析见解
        
        报告结构要求：
        1. 执行摘要（Executive Summary）
        2. 研究背景和现状（Background & Current State）
        3. 核心技术发现（Key Technical Findings）
           - 学术前沿（Academic Frontiers）
           - 产业应用（Industrial Applications）
        4. 深度分析（In-depth Analysis）
           - 技术对比分析
           - 优势与挑战
           - 学术与产业的差距分析
        5. 未来趋势预测（Future Trends）
        6. 结论和建议（Conclusions & Recommendations）
        7. 参考文献（References）
           - Web来源
           - 学术论文
        
        质量要求：
        - 使用学术化但易读的语言
        - 逻辑清晰，论证有力
        - 包含具体的技术细节和数据
        - 所有引用使用Markdown链接格式
        - 总字数不少于2000字
        - 确保信息的准确性和时效性
        
        研究主题：{topic}
        Web搜索结果：{web_results}
        arXiv搜索结果：{arxiv_results}""" + (f"""
        
        验证反馈：{validation_feedback}
        注意：请根据上述验证反馈改进报告质量。""" if validation_feedback else ""),
        agent=research_analyst,
        expected_output="""
        一份完整的高质量Markdown格式研究报告，结构如下：
        
        # [报告标题] - 基于并发搜索的综合分析报告
        
        ## 执行摘要
        [5-8句话概括核心发现、主要趋势和关键结论，突出学术和产业两个维度的重要发现]
        
        ## 1. 研究背景和现状
        [介绍研究主题的重要性、背景和当前发展状况]
        
        ## 2. 核心技术发现
        
        ### 2.1 学术前沿进展
        [基于arXiv论文的最新学术研究进展]
        - 突破性技术：[具体技术内容]
        - 研究热点：[当前研究焦点]
        - 理论创新：[理论贡献和创新]
        
        ### 2.2 产业应用现状
        [基于Web搜索的产业应用和商业化进展]
        - 商业化产品：[具体产品和服务]
        - 市场趋势：[市场发展动态]
        - 应用场景：[实际应用情况]
        
        ## 3. 深度分析
        
        ### 3.1 技术对比分析
        [不同技术方案的详细对比]
        
        ### 3.2 优势与挑战
        [客观分析技术优势和面临的挑战]
        
        ### 3.3 学术与产业差距分析
        [分析理论研究与实际应用之间的差距]
        
        ## 4. 未来趋势预测
        [基于当前发现的未来发展趋势预测]
        - 短期趋势（1-2年）
        - 中期趋势（3-5年）
        - 长期展望（5年以上）
        
        ## 5. 结论和建议
        [总结性结论和实用建议]
        - 主要结论
        - 研究建议
        - 应用建议
        
        ## 6. 参考文献
        
        ### Web来源
        - [来源1标题](URL) - 访问日期：[日期]
        - [来源2标题](URL) - 访问日期：[日期]
        ...
        
        ### 学术论文
        - [论文1] Author et al. - arXiv:[ID] - [发布日期]
        - [论文2] Author et al. - arXiv:[ID] - [发布日期]
        ...
        
        ---
        *报告生成时间：[时间戳]*  
        *执行模式：并发搜索整合分析*
        """
    )


# 任务依赖关系配置
TASK_DEPENDENCIES = {
    'planning': [],  # 规划任务无依赖
    'execution': ['planning'],  # 执行任务依赖规划任务
    'analysis': ['execution'],  # 分析任务依赖执行任务
    'validation': ['analysis'],  # 验证任务依赖分析任务
    # 并发模式的任务依赖
    'web_search': ['planning'],  # Web搜索依赖规划
    'arxiv_search': ['planning'],  # arXiv搜索依赖规划
    'integrated_analysis': ['web_search', 'arxiv_search']  # 整合分析依赖两个搜索任务
}
