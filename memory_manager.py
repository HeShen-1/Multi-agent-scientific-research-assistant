#!/usr/bin/env python3
"""
记忆管理工具
提供记忆库的管理和查看功能
"""

import asyncio
from datetime import datetime
from tools.memory_tool import get_memory_manager, recall_past_research, store_research_memory, memory_stats


def show_memory_stats():
    """显示记忆库统计信息"""
    print("📊 记忆库统计信息")
    print("="*50)
    
    try:
        stats_info = memory_stats.invoke({})
        print(stats_info)
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")


def search_memories():
    """交互式搜索记忆"""
    print("\n🔍 搜索历史研究记忆")
    print("="*50)
    
    while True:
        query = input("请输入搜索关键词（输入'q'退出）: ").strip()
        if query.lower() == 'q':
            break
        
        if not query:
            print("⚠️ 请输入搜索关键词")
            continue
        
        try:
            results = recall_past_research.invoke({"query": query, "max_results": 5})
            print("\n" + "="*50)
            print(results)
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")


def add_test_memory():
    """添加测试记忆"""
    print("\n📝 添加测试研究记忆")
    print("="*50)
    
    test_memories = [
        {
            "topic": "深度学习模型压缩技术",
            "content": """# 深度学习模型压缩技术研究报告

## 执行摘要
深度学习模型压缩是提高模型部署效率的关键技术，主要包括剪枝、量化、知识蒸馏和低秩分解等方法。

## 核心技术发现
### 模型剪枝
- 结构化剪枝：移除整个通道或层
- 非结构化剪枝：移除单个权重
- 动态剪枝：运行时自适应调整

### 模型量化
- 权重量化：将32位浮点数转换为8位整数
- 激活量化：压缩中间激活值
- 混合精度：不同层使用不同精度

### 知识蒸馏
- 教师-学生模型框架
- 特征匹配和响应匹配
- 自蒸馏技术

## 参考文献
- [模型压缩综述](https://arxiv.org/abs/1710.09282)
- [知识蒸馏原理](https://arxiv.org/abs/1503.02531)
""",
            "additional_info": "测试数据，执行模式：手动添加"
        },
        {
            "topic": "联邦学习隐私保护机制",
            "content": """# 联邦学习隐私保护机制研究报告

## 执行摘要
联邦学习通过分布式训练保护数据隐私，但仍面临模型推理攻击、成员推理攻击等隐私风险。

## 核心技术发现
### 差分隐私
- 添加噪声保护个体隐私
- 隐私预算管理
- 组合隐私损失计算

### 同态加密
- 加密状态下的计算
- 计算开销较大
- 适用于高隐私要求场景

### 安全多方计算
- 秘密共享协议
- 无需信任第三方
- 通信开销较高

## 未来发展趋势
- 轻量级隐私保护算法
- 隐私保护与模型性能的平衡
- 跨域联邦学习标准化

## 参考文献
- [联邦学习综述](https://arxiv.org/abs/1912.04977)
- [差分隐私机制](https://arxiv.org/abs/1909.05830)
""",
            "additional_info": "测试数据，执行模式：手动添加"
        }
    ]
    
    for i, memory in enumerate(test_memories, 1):
        print(f"添加测试记忆 {i}: {memory['topic']}")
        try:
            result = store_research_memory.invoke({
                "topic": memory["topic"],
                "content": memory["content"],
                "additional_info": memory["additional_info"]
            })
            print(f"  {result}")
        except Exception as e:
            print(f"  ❌ 添加失败: {e}")
    
    print("\n✅ 测试记忆添加完成")


def clear_memories():
    """清空记忆库"""
    print("\n🧹 清空记忆库")
    print("="*50)
    
    confirm = input("⚠️ 这将删除所有记忆数据，确认吗？(输入'YES'确认): ").strip()
    if confirm == "YES":
        try:
            memory_manager = get_memory_manager()
            success = memory_manager.clear_memories(confirm=True)
            if success:
                print("✅ 记忆库已清空")
            else:
                print("❌ 清空失败")
        except Exception as e:
            print(f"❌ 清空记忆库失败: {e}")
    else:
        print("取消操作")


async def test_memory_in_research():
    """测试记忆功能在研究中的应用"""
    print("\n🧪 测试记忆功能在研究流程中的应用")
    print("="*50)
    
    # 导入异步研究函数
    from main import run_parallel_research
    
    # 测试相关主题
    test_topics = [
        "深度学习模型优化技术",  # 与已有记忆相关
        "联邦学习最新进展",      # 与已有记忆相关
        "量子计算算法应用"       # 全新主题
    ]
    
    for topic in test_topics:
        print(f"\n🔬 测试主题: {topic}")
        print("-" * 30)
        
        try:
            # 运行研究（会自动使用记忆功能）
            result = await run_parallel_research(topic)
            
            # 检查结果长度
            if len(result) > 100:
                print(f"✅ 研究完成，报告长度: {len(result)}字符")
                # 显示是否有记忆相关的内容
                if "历史研究" in result or "过往研究" in result:
                    print("🧠 检测到记忆功能被使用")
                else:
                    print("📝 未检测到明显的记忆使用痕迹")
            else:
                print(f"⚠️ 研究可能未完全完成，报告长度: {len(result)}字符")
                
        except Exception as e:
            print(f"❌ 研究测试失败: {e}")
        
        print()


def main():
    """主菜单"""
    while True:
        print("\n🧠 多智能体科研助手 - 记忆管理工具")
        print("="*60)
        print("1. 查看记忆库统计")
        print("2. 搜索历史记忆")
        print("3. 添加测试记忆")
        print("4. 测试记忆功能")
        print("5. 清空记忆库")
        print("0. 退出")
        print("="*60)
        
        choice = input("请选择操作 (0-5): ").strip()
        
        if choice == "0":
            print("👋 退出记忆管理工具")
            break
        elif choice == "1":
            show_memory_stats()
        elif choice == "2":
            search_memories()
        elif choice == "3":
            add_test_memory()
        elif choice == "4":
            print("⚠️ 注意：此测试需要API密钥且可能产生费用")
            confirm = input("是否继续？(y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                asyncio.run(test_memory_in_research())
        elif choice == "5":
            clear_memories()
        else:
            print("❌ 无效选择，请重试")


if __name__ == "__main__":
    main()
