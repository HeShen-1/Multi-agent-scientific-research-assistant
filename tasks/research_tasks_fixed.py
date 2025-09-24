"""
多智能体科研助手的任务定义（修复版本）
修复了validation_feedback模板变量问题
"""

from crewai import Task


def create_integrated_analysis_task_fixed(research_analyst, topic: str, validation_feedback: str = "") -> Task:
    """
    创建整合分析任务（修复版本，解决validation_feedback模板变量问题）
    
    Args:
        research_analyst: Research Analyst智能体实例
        topic: 研究主题
        validation_feedback: 可选的验证反馈信息
        
    Returns:
        Task: 整合分析任务实例
    """
    # 构建基础任务描述
    base_description = f"""
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
        Web搜索结果：{{web_results}}
        arXiv搜索结果：{{arxiv_results}}"""
    
    # 如果提供了验证反馈，添加到描述中
    if validation_feedback:
        base_description += f"""
        
        验证反馈：{validation_feedback}
        注意：请根据上述验证反馈改进报告质量。"""
    
    return Task(
        description=base_description,
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
