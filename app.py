"""
多智能体科研助手Web界面
基于Streamlit的用户友好界面

运行命令：streamlit run app.py
"""

import streamlit as st
import os
import sys
from datetime import datetime
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主程序功能
from main import load_environment, run_research, validate_topic, save_report

# 配置页面
st.set_page_config(
    page_title="多智能体科研助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1e88e5;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1565c0;
        transform: translateY(-2px);
        transition: all 0.3s;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if 'research_history' not in st.session_state:
        st.session_state.research_history = []
    if 'current_report' not in st.session_state:
        st.session_state.current_report = ""
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
    if 'redo_topic' not in st.session_state:
        st.session_state.redo_topic = ""
    if 'memory_search_results' not in st.session_state:
        st.session_state.memory_search_results = None


def display_header():
    """显示页面头部"""
    st.markdown('<div class="main-header">📖 多智能体科研助手</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **🚀 欢迎使用多智能体科研助手！**
    
    这是一个基于CrewAI的智能研究系统，能够：
    - 🔍 自动搜索Web和学术数据库
    - 🌚 多智能体协作分析
    - 📊 生成结构化研究报告
    - 📝 提供详细的引用来源
    """)
    st.markdown('</div>', unsafe_allow_html=True)


def display_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.header("⚙️ 系统配置")
        
        # 环境检查
        st.subheader("🔑 API密钥状态")
        
        # 加载环境变量
        load_dotenv()
        
        openai_key = os.getenv('OPENAI_API_KEY')
        tavily_key = os.getenv('TAVILY_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com/v1')
        api_tavily = os.getenv('TAVILY_API_BASE', 'https://app.tavily.com/home')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
        
        if openai_key:
            st.success(f"✅ DeepSeek API 已配置 ({model_name})")
            st.info(f"🔗 API端点: {api_base}")
        else:
            st.error("❌ DeepSeek API 未配置")
            
        if tavily_key:
            st.success("✅ Tavily API 已配置")
            st.info(f"🔗 API端点: {api_tavily}")
        else:
            st.warning("⚠️ Tavily API 未配置（将使用备用搜索）")
        
        st.markdown("---")
        
        # 系统设置
        st.subheader("🛠️ 高级设置")
        
        model_name = st.selectbox(
            "选择LLM模型",
            ["deepseek-chat", "deepseek-coder"],
            index=0,
            help="DeepSeek模型选择：deepseek-chat适合通用对话，deepseek-coder适合代码相关任务"
        )
        
        max_results = st.slider(
            "最大搜索结果数",
            min_value=3,
            max_value=10,
            value=5,
            help="每个搜索查询返回的最大结果数量"
        )
        
        verbose_mode = st.checkbox(
            "详细输出模式",
            value=True,
            help="显示智能体的详细思考过程"
        )
        
        st.markdown("---")
        
        # 研究历史与记忆管理
        st.subheader("📚 研究历史与记忆")
        
        # # 记忆库统计
        # try:
        #     from tools.memory_tool import memory_stats
        #     stats_result = memory_stats.invoke({})
            
        #     # 提取统计数字
        #     if "总记忆数量:" in stats_result:
        #         memory_count = stats_result.split("总记忆数量:")[1].split("\n")[0].strip()
        #         storage_type = stats_result.split("存储类型:")[1].split("\n")[0].strip()
                
        #         col1, col2 = st.columns(2)
        #         with col1:
        #             st.metric("🧠 记忆总数", memory_count)
        #         with col2:
        #             st.metric("💾 存储类型", storage_type)
        #     else:
        #         st.info("📊 记忆库统计: 正在初始化...")
                
        # except Exception as e:
        #     st.warning(f"⚠️ 记忆库连接异常: {str(e)[:50]}...")
        
        # 搜索历史记忆
        search_query = st.text_input(
            "🔍 搜索历史研究:",
            placeholder="输入关键词搜索...",
            help="搜索已存储的历史研究记忆"
        )
        
        if search_query:
            try:
                from tools.memory_tool import recall_past_research
                search_result = recall_past_research.invoke({
                    "query": search_query,
                    "max_results": 3
                })
                
                if "未找到" in search_result:
                    st.info("📭 未找到相关历史研究")
                else:
                    with st.expander("🔍 搜索结果", expanded=True):
                        st.markdown(search_result)
                        
            except Exception as e:
                st.error(f"❌ 搜索失败: {str(e)}")
        
        st.markdown("---")
        
        # 当前会话历史
        st.subheader("📋 当前会话历史")
        if st.session_state.research_history:
            # 显示统计
            total_research = len(st.session_state.research_history)
            completed_research = len([r for r in st.session_state.research_history if r['status'] == '完成'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 总研究数", total_research)
            with col2:
                st.metric("✅ 成功完成", completed_research)
            
            # 显示详细历史
            for i, item in enumerate(reversed(st.session_state.research_history[-5:])):
                status_icon = "✅" if item['status'] == '完成' else "❌"
                
                with st.expander(f"{status_icon} {item['topic'][:25]}..."):
                    st.write(f"**📅 时间**: {item['timestamp']}")
                    st.write(f"**📊 状态**: {item['status']}")
                    
                    if item['filepath'] and item['status'] == '完成':
                        st.write(f"**📁 文件**: `{item['filepath']}`")
                        
                        # 操作按钮
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"📖 查看", key=f"view_{i}"):
                                try:
                                    with open(item['filepath'], 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    st.session_state.current_report = content
                                    st.success("✅ 报告已加载到主界面")
                                except Exception as e:
                                    st.error(f"❌ 读取失败: {e}")
                        
                        with col2:
                            if st.button(f"📥 下载", key=f"download_{i}"):
                                try:
                                    with open(item['filepath'], 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    st.download_button(
                                        label="📥 下载文件",
                                        data=content,
                                        file_name=os.path.basename(item['filepath']),
                                        mime="text/markdown",
                                        key=f"dl_btn_{i}"
                                    )
                                except Exception as e:
                                    st.error(f"❌ 下载失败: {e}")
                        
                        with col3:
                            if st.button(f"🔄 重做", key=f"redo_{i}"):
                                st.session_state.redo_topic = item['topic']
                                st.success("✅ 主题已填入输入框")
                    
                    elif item['status'] == '失败':
                        st.error("❌ 研究失败，可以尝试重新研究该主题")
                        if st.button(f"🔄 重试", key=f"retry_{i}"):
                            st.session_state.redo_topic = item['topic']
                            st.success("✅ 主题已填入输入框")
            
            # 清空历史按钮
            if st.button("🗑️ 清空会话历史", help="清空当前会话的研究历史"):
                st.session_state.research_history = []
                st.success("✅ 会话历史已清空")
                st.rerun()
                
        else:
            st.info("📝 当前会话暂无研究历史")
        
        # 记忆管理操作
        st.markdown("---")
        st.subheader("🛠️ 记忆管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 查看统计", help="查看详细的记忆库统计信息"):
                try:
                    from tools.memory_tool import memory_stats
                    detailed_stats = memory_stats.invoke({})
                    st.text_area("📊 详细统计", detailed_stats, height=100)
                except Exception as e:
                    st.error(f"❌ 获取统计失败: {e}")
        
        with col2:
            if st.button("🧹 管理工具", help="打开记忆管理工具"):
                st.info("💡 在终端运行: `python memory_manager.py`")
                st.code("python memory_manager.py", language="bash")


def display_main_interface():
    """显示主界面"""
    # 检查环境
    if not load_environment():
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.error("❌ 环境配置不完整，请检查.env文件中的API密钥配置")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("📋 配置指南"):
            st.markdown("""
            请按以下步骤配置环境：
            
            1. 复制 `env_example.txt` 为 `.env`
            2. 在 `.env` 文件中填入您的API密钥：
               ```
               OPENAI_API_KEY="sk-your-deepseek-api-key"
               OPENAI_API_BASE="https://api.deepseek.com"
               OPENAI_MODEL_NAME="deepseek-chat"
               TAVILY_API_KEY="tvly-your-tavily-api-key"
               ```
            3. 重启应用
            
            **获取DeepSeek API密钥：**
            - 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
            - 注册账户并获取API密钥
            """)
        return
    
    # 主要功能区域
    st.header("🔬 开始新的研究")
    
    # 研究主题输入
    # 检查是否有重做主题
    default_value = st.session_state.redo_topic if st.session_state.redo_topic else ""
    if st.session_state.redo_topic:
        st.info(f"📝 已填入历史主题: {st.session_state.redo_topic}")
        st.session_state.redo_topic = ""  # 清空重做状态
    
    topic = st.text_area(
        "请输入您想要研究的主题：",
        value=default_value,
        height=100,
        placeholder="例如：大语言模型的上下文窗口扩展技术",
        help="请详细描述您想要研究的技术主题，越具体越好"
    )
    
    # 智能推荐功能
    if topic and len(topic) > 5:
        with st.expander("💡 智能推荐", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 查找相关历史"):
                    try:
                        from tools.memory_tool import recall_past_research
                        recommendations = recall_past_research.invoke({
                            "query": topic,
                            "max_results": 2
                        })
                        
                        if "未找到" not in recommendations:
                            st.markdown("**🧠 基于历史记忆的相关研究:**")
                            st.markdown(recommendations)
                        else:
                            st.info("📭 暂无相关历史研究，将进行全新探索")
                            
                    except Exception as e:
                        st.warning(f"⚠️ 推荐功能暂时不可用: {str(e)[:30]}...")
            
            with col2:
                st.markdown("**🚀 研究优化建议:**")
                if "深度学习" in topic or "机器学习" in topic:
                    st.markdown("- 建议关注最新的模型架构\n- 包含性能对比分析\n- 考虑实际部署场景")
                elif "算法" in topic:
                    st.markdown("- 重点分析时间复杂度\n- 对比不同实现方案\n- 包含算法优化策略")
                else:
                    st.markdown("- 确保主题具体明确\n- 包含最新技术发展\n- 考虑实际应用价值")
    
    # 研究选项
    col1, col2 = st.columns(2)
    
    with col1:
        include_recent = st.checkbox(
            "重点关注最新进展",
            value=True,
            help="优先搜索最近1-2年的研究成果"
        )
        
    with col2:
        include_industry = st.checkbox(
            "包含产业应用",
            value=True,
            help="搜索相关的产业应用和商业案例"
        )
    
    # 开始研究按钮
    if st.button("🚀 开始研究", disabled=st.session_state.research_running):
        if not validate_topic(topic):
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error("❌ 请输入有效的研究主题（至少5个字符）")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 开始研究
            st.session_state.research_running = True
            st.session_state.current_report = ""
            
            # 显示进度
            with st.spinner("🤖 智能体团队正在工作中..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 模拟进度更新
                    status_text.text("📋 Research Manager 正在制定研究计划...")
                    progress_bar.progress(20)
                    
                    # 执行研究
                    result = run_research(topic)
                    
                    progress_bar.progress(70)
                    status_text.text("📝 Research Analyst 正在撰写报告...")
                    
                    # 保存报告
                    filepath = save_report(result, topic)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ 研究完成！")
                    
                    # 更新会话状态
                    st.session_state.current_report = result
                    st.session_state.research_history.append({
                        'topic': topic,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': '完成',
                        'filepath': filepath
                    })
                    
                    st.session_state.research_running = False
                    
                    # 显示成功消息
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success(f"✅ 研究完成！报告已保存到: {filepath}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.session_state.research_running = False
                    progress_bar.progress(0)
                    status_text.text("")
                    
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ 研究过程中发生错误: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 记录错误
                    st.session_state.research_history.append({
                        'topic': topic,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': '失败',
                        'filepath': None
                    })


def display_results():
    """显示研究结果"""
    if st.session_state.current_report:
        st.header("📊 研究报告")
        
        # 报告标签页
        tab1, tab2, tab3 = st.tabs(["📖 完整报告", "📋 报告摘要", "💾 下载"])
        
        with tab1:
            st.markdown(st.session_state.current_report)
            
        with tab2:
            # 提取报告摘要（前1000字符）
            summary = st.session_state.current_report[:1000]
            if len(st.session_state.current_report) > 1000:
                summary += "\n\n... [查看完整报告获取更多内容]"
            st.markdown(summary)
            
        with tab3:
            st.download_button(
                label="📥 下载Markdown报告",
                data=st.session_state.current_report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            # 显示报告统计
            word_count = len(st.session_state.current_report.split())
            char_count = len(st.session_state.current_report)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 字数", f"{word_count:,}")
            with col2:
                st.metric("🔤 字符数", f"{char_count:,}")
            with col3:
                # 估算阅读时间（假设每分钟200字）
                read_time = max(1, word_count // 200)
                st.metric("⏱️ 阅读时间", f"{read_time}分钟")


def main():
    """主函数"""
    init_session_state()
    display_header()
    display_sidebar()
    display_main_interface()
    display_results()
    
    # 页脚
    st.markdown("---")
    
    # 功能特性说明
    with st.expander("📖 功能特性", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 多智能体协作**
            - Research Manager: 规划协调
            - Senior Researcher: 信息搜集
            - Research Analyst: 深度分析
            """)
        
        with col2:
            st.markdown("""
            **🧠 长期记忆功能**
            - 自动保存研究结果
            - 智能搜索历史记忆
            - 避免重复研究
            """)
        
        with col3:
            st.markdown("""
            **⚡ 高性能执行**
            - 并发搜索优化
            - 异步I/O处理
            - 智能缓存机制
            """)
    
    st.markdown(
        '<div style="text-align: center; color: #666; padding: 2rem;">'
        '🤖 多智能体科研助手 v1.1 (Memory Enhanced) | 基于CrewAI + ChromaDB构建 | '
        '<a href="https://github.com/your-repo" target="_blank">GitHub</a>'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
