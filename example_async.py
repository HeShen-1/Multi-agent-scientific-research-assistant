#!/usr/bin/env python3
"""
异步并发功能使用示例
演示如何使用多智能体科研助手的三种执行模式
"""

import asyncio
from main import run_research_sync, run_research_async, run_parallel_research, run_parallel_research_with_validation

async def demo_single_research():
    """演示单个研究主题的四种执行模式"""
    topic = "边缘计算在物联网中的应用"
    
    print("🔬 单主题研究演示")
    print("="*50)
    print(f"研究主题: {topic}\n")
    
    # 1. 验证模式（新增，推荐）
    print("🔍 模式1: 验证模式（推荐）")
    try:
        result = await run_parallel_research_with_validation(topic)
        print(f"✅ 验证模式完成，报告长度: {len(result)}字符")
        if "验证通过" in result:
            print("   🎯 质量验证：通过")
        elif "部分验证" in result:
            print("   ⚠️ 质量验证：部分通过")
    except Exception as e:
        print(f"❌ 验证模式失败: {e}")
    
    print()
    
    # 2. 高级并发模式
    print("🚀 模式2: 高级并发模式")
    try:
        result = await run_parallel_research(topic)
        print(f"✅ 并发模式完成，报告长度: {len(result)}字符")
    except Exception as e:
        print(f"❌ 并发模式失败: {e}")
    
    print()
    
    # 3. 异步模式
    print("⚡ 模式3: 异步模式") 
    try:
        result = await run_research_async(topic)
        print(f"✅ 异步模式完成，报告长度: {len(result)}字符")
    except Exception as e:
        print(f"❌ 异步模式失败: {e}")
    
    print()
    
    # 4. 传统同步模式
    print("🐌 模式4: 传统同步模式")
    try:
        result = run_research_sync(topic)
        print(f"✅ 同步模式完成，报告长度: {len(result)}字符")
    except Exception as e:
        print(f"❌ 同步模式失败: {e}")

async def demo_batch_research():
    """演示批量并发研究"""
    topics = [
        "量子计算在密码学中的应用",
        "5G网络切片技术发展",
        "联邦学习隐私保护机制"
    ]
    
    print("\n" + "="*50)
    print("🔄 批量并发研究演示")
    print("="*50)
    print(f"同时研究 {len(topics)} 个主题:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic}")
    print()
    
    # 并发执行所有研究
    print("🚀 开始并发批量研究...")
    try:
        tasks = [run_parallel_research(topic) for topic in topics]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        print("📊 批量研究结果:")
        for i, (topic, result) in enumerate(zip(topics, results), 1):
            if isinstance(result, Exception):
                print(f"  {i}. ❌ {topic}: 失败 - {result}")
            else:
                print(f"  {i}. ✅ {topic}: 成功 ({len(result)}字符)")
                
    except Exception as e:
        print(f"❌ 批量研究失败: {e}")

async def demo_custom_workflow():
    """演示自定义工作流"""
    print("\n" + "="*50)
    print("⚙️  自定义工作流演示")
    print("="*50)
    
    # 分阶段执行，可以在中间添加自定义逻辑
    topic = "AI大模型的能耗优化技术"
    print(f"研究主题: {topic}")
    
    try:
        print("\n📋 阶段1: 研究规划...")
        # 这里可以调用单独的规划阶段（需要实现相应接口）
        print("✅ 规划完成")
        
        print("🔍 阶段2: 并发信息搜集...")
        # 这里可以调用并发搜索（需要实现相应接口）
        print("✅ 信息搜集完成")
        
        print("📝 阶段3: 深度分析...")
        # 最终调用完整流程
        result = await run_parallel_research(topic)
        print(f"✅ 自定义工作流完成，生成报告: {len(result)}字符")
        
    except Exception as e:
        print(f"❌ 自定义工作流失败: {e}")

async def demo_memory_features():
    """演示记忆功能"""
    print("\n" + "="*50)
    print("🧠 记忆功能演示")
    print("="*50)
    
    # 导入记忆工具
    from tools.memory_tool import recall_past_research, store_research_memory, memory_stats
    
    print("📊 当前记忆库状态:")
    try:
        stats = memory_stats()
        print(stats)
    except Exception as e:
        print(f"❌ 获取记忆统计失败: {e}")
    
    print("\n🔍 搜索历史研究:")
    test_queries = ["深度学习", "模型压缩", "联邦学习"]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        try:
            result = recall_past_research(query)
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    print("\n📝 演示相关主题研究（会利用记忆）:")
    topics = [
        "深度学习模型压缩最新技术",  # 可能与历史记忆相关
        "区块链共识算法创新"        # 全新主题
    ]
    
    for topic in topics:
        print(f"\n🔬 研究主题: {topic}")
        try:
            result = await run_parallel_research(topic)
            print(f"✅ 完成，报告长度: {len(result)}字符")
            if "历史研究" in result or "过往研究" in result:
                print("🧠 检测到使用了历史记忆")
        except Exception as e:
            print(f"❌ 研究失败: {e}")

async def demo_validation_features():
    """演示验证功能特性"""
    print("\n" + "="*50)
    print("🔍 验证功能特性演示")
    print("="*50)
    
    # 选择一个相对复杂的主题来测试验证功能
    topic = "大语言模型的幻觉问题及解决方案"
    
    print(f"🎯 测试主题: {topic}")
    print("   （选择此主题是因为它容易产生需要验证的技术声明）")
    
    print("\n🔄 验证工作流程:")
    print("   1. 规划阶段 - 制定搜索策略")
    print("   2. 并发搜索 - Web + arXiv 同时进行")
    print("   3. 分析阶段 - 生成初步报告")
    print("   4. 验证阶段 - 事实核查和质量控制")
    print("   5. 改进循环 - 根据验证反馈优化报告（最多3次）")
    
    try:
        print("\n🚀 开始验证模式研究...")
        result = await run_parallel_research_with_validation(topic)
        
        print("\n📊 验证结果分析:")
        
        # 分析验证相关信息
        lines = result.split('\n')
        metadata_section = []
        in_metadata = False
        
        for line in lines:
            if line.strip() == '---':
                in_metadata = not in_metadata
            elif in_metadata:
                metadata_section.append(line)
        
        # 提取关键信息
        for line in metadata_section:
            if '验证状态:' in line:
                print(f"   {line.strip()}")
            elif '执行模式:' in line:
                print(f"   {line.strip()}")
            elif '执行时间:' in line:
                print(f"   {line.strip()}")
        
        # 保存验证演示报告
        filename = "validation_demo_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n📄 验证演示报告已保存: {filename}")
        
        # 显示报告摘要
        print(f"\n📋 报告统计:")
        print(f"   - 总字符数: {len(result):,}")
        print(f"   - 总行数: {len(lines):,}")
        
        # 检查验证标识
        validation_keywords = ['验证', '事实核查', '质量控制', '准确性']
        found_keywords = sum(1 for keyword in validation_keywords if keyword in result)
        print(f"   - 验证相关关键词: {found_keywords}/{len(validation_keywords)}个")
        
    except Exception as e:
        print(f"❌ 验证功能演示失败: {e}")

def main():
    """主函数"""
    print("🤖 多智能体科研助手 - 异步并发功能演示")
    print("="*60)
    print("⚠️  注意：运行此演示需要配置API密钥")
    print("     请确保 .env 文件中设置了正确的 OPENAI_API_KEY")
    print("="*60)
    
    # 检查是否要运行演示
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 未检测到API密钥，演示将会失败")
        print("   请确保:")
        print("   1. 在项目根目录创建 .env 文件")
        print("   2. 在 .env 文件中设置 OPENAI_API_KEY='您的DeepSeek密钥'")
        print("   3. 或运行 'python setup_env.py' 来配置环境")
        return
    
    print("✅ 检测到API密钥，开始演示...\n")
    
    # 运行所有演示
    asyncio.run(demo_single_research())
    asyncio.run(demo_batch_research()) 
    asyncio.run(demo_memory_features())
    asyncio.run(demo_validation_features())  # 新增验证功能演示
    asyncio.run(demo_custom_workflow())
    
    print("\n" + "="*60)
    print("🎉 演示完成！")
    print("\n💡 使用建议:")
    print("   - 生产环境推荐使用验证模式确保最高质量")
    print("   - 开发调试时可使用同步模式便于排错")
    print("   - 批量处理时注意控制并发数量避免API限流")
    print("   - 验证模式会增加执行时间但显著提升报告准确性")

if __name__ == "__main__":
    main()
