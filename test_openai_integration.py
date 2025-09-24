#!/usr/bin/env python3
"""
OpenAI SDK集成测试脚本
Test script for OpenAI SDK integration

验证新的OpenAI SDK调用是否正常工作
"""

import os
import sys
from dotenv import load_dotenv

def test_openai_sdk_integration():
    """测试OpenAI SDK集成"""
    print("🧪 测试OpenAI SDK集成...")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    try:
        # 测试导入
        from agents.research_agents import (
            get_model_config, 
            create_openai_client, 
            get_model_name,
            test_openai_client
        )
        print("✅ 导入新的函数成功")
        
        # 测试配置获取
        config = get_model_config()
        print(f"✅ 模型配置获取成功:")
        print(f"   - API Key: {config['api_key'][:10]}...{config['api_key'][-4:]}")
        print(f"   - Base URL: {config['base_url']}")
        print(f"   - Model: {config['model']}")
        
        # 测试客户端创建
        client = create_openai_client()
        print(f"✅ OpenAI客户端创建成功: {type(client)}")
        
        # 测试模型名称获取（保持向后兼容）
        model_name = get_model_name()
        print(f"✅ 模型名称获取成功: {model_name}")
        
        # 测试实际API调用
        print("\n🔄 测试API调用...")
        success = test_openai_client()
        
        if success:
            print("🎉 所有测试通过！OpenAI SDK集成成功！")
            return True
        else:
            print("❌ API调用测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crewai_compatibility():
    """测试与CrewAI的兼容性"""
    print("\n🤝 测试CrewAI兼容性...")
    print("=" * 50)
    
    try:
        from agents.research_agents import create_research_manager, create_crewai_compatible_llm
        
        # 测试LLM创建
        llm = create_crewai_compatible_llm()
        print(f"✅ CrewAI兼容LLM创建成功: {type(llm)}")
        
        # 如果是ChatOpenAI实例，显示模型名称
        if hasattr(llm, 'model_name'):
            print(f"   - 模型名称: {llm.model_name}")
        elif hasattr(llm, 'model'):
            print(f"   - 模型名称: {llm.model}")
        
        # 尝试创建智能体
        agent = create_research_manager()
        print(f"✅ 智能体创建成功: {agent.role}")
        print(f"   - LLM: {type(agent.llm) if hasattr(agent, 'llm') else 'N/A'}")
        
        # 如果智能体有LLM，显示其模型信息
        if hasattr(agent, 'llm') and hasattr(agent.llm, 'model_name'):
            print(f"   - 智能体LLM模型: {agent.llm.model_name}")
        elif hasattr(agent, 'llm') and hasattr(agent.llm, 'model'):
            print(f"   - 智能体LLM模型: {agent.llm.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ CrewAI兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 OpenAI SDK集成验证测试")
    print("Testing OpenAI SDK Integration")
    print("=" * 60)
    
    # 测试OpenAI SDK集成
    sdk_test_passed = test_openai_sdk_integration()
    
    # 测试CrewAI兼容性
    crewai_test_passed = test_crewai_compatibility()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   - OpenAI SDK集成: {'✅ 通过' if sdk_test_passed else '❌ 失败'}")
    print(f"   - CrewAI兼容性: {'✅ 通过' if crewai_test_passed else '❌ 失败'}")
    
    if sdk_test_passed and crewai_test_passed:
        print("\n🎉 所有测试通过！系统已成功迁移到OpenAI SDK！")
        print("💡 现在可以运行主程序: python main.py")
        return True
    else:
        print("\n❌ 部分测试失败，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
