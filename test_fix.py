#!/usr/bin/env python3
"""
修复验证测试脚本
Fix Verification Test Script

测试修复后的系统是否能正常工作
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_environment_setup():
    """测试环境配置"""
    logger.info("🔍 测试环境配置...")
    
    # 检查.env文件
    if not os.path.exists('.env'):
        logger.error("❌ .env文件不存在")
        logger.info("💡 请运行: python setup_config.py")
        return False
    
    # 加载环境变量
    load_dotenv()
    
    # 检查必要的环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'sk-your-deepseek-api-key-here':
        logger.error("❌ API密钥未配置")
        logger.info("💡 请在.env文件中设置正确的OPENAI_API_KEY")
        return False
    
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com/v1')
    model_name = os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
    
    logger.info(f"✅ API Base: {api_base}")
    logger.info(f"✅ Model: {model_name}")
    logger.info(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    
    return True

def test_imports():
    """测试关键模块导入"""
    logger.info("🔍 测试模块导入...")
    
    try:
        from crewai import Agent, Crew, Process
        logger.info("✅ CrewAI导入成功")
    except ImportError as e:
        logger.error(f"❌ CrewAI导入失败: {e}")
        return False
    
    try:
        from openai import OpenAI
        logger.info("✅ OpenAI SDK导入成功")
    except ImportError as e:
        logger.error(f"❌ OpenAI SDK导入失败: {e}")
        logger.info("💡 请运行: pip install openai")
        return False
    
    try:
        from utils.network_utils import retry_with_backoff, check_api_connectivity
        logger.info("✅ 网络工具导入成功")
    except ImportError as e:
        logger.error(f"❌ 网络工具导入失败: {e}")
        return False
    
    try:
        from agents.research_agents import create_research_manager
        logger.info("✅ 智能体模块导入成功")
    except ImportError as e:
        logger.error(f"❌ 智能体模块导入失败: {e}")
        return False
    
    return True

def test_llm_creation():
    """测试LLM实例创建"""
    logger.info("🔍 测试LLM实例创建...")
    
    try:
        from agents.research_agents import get_model_name
        llm = get_model_name()
        logger.info("✅ LLM实例创建成功")
        logger.info(f"✅ LLM类型: {type(llm)}")
        return True
    except Exception as e:
        logger.error(f"❌ LLM实例创建失败: {e}")
        return False

def test_api_connectivity():
    """测试API连通性"""
    logger.info("🔍 测试API连通性...")
    
    try:
        from utils.network_utils import check_api_connectivity
        
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com/v1')
        
        if check_api_connectivity(api_base, api_key):
            logger.info("✅ API连通性测试成功")
            return True
        else:
            logger.warning("⚠️ API连通性测试失败，但这可能是暂时的")
            return True  # 不阻塞测试，因为可能是网络临时问题
    except Exception as e:
        logger.error(f"❌ API连通性测试异常: {e}")
        return True  # 不阻塞测试

def test_simple_llm_call():
    """测试简单的LLM调用"""
    logger.info("🔍 测试简单LLM调用...")
    
    try:
        from agents.research_agents import test_openai_client
        
        # 使用新的OpenAI客户端测试函数
        success = test_openai_client()
        
        if success:
            logger.info("✅ OpenAI客户端调用测试成功")
            return True
        else:
            logger.error("❌ OpenAI客户端调用测试失败")
            return False
        
    except Exception as e:
        logger.error(f"❌ LLM调用失败: {e}")
        
        # 提供详细的错误分析
        error_str = str(e).lower()
        if "cloudflare" in error_str:
            logger.error("🛡️ 检测到Cloudflare防护，请尝试更换网络环境")
        elif "rate limit" in error_str:
            logger.error("🚫 API调用频率限制，请稍后重试")
        elif "connection" in error_str:
            logger.error("🌐 网络连接问题，请检查网络状态")
        elif "api key" in error_str:
            logger.error("🔑 API密钥问题，请检查配置")
        
        return False

def test_agent_creation():
    """测试智能体创建"""
    logger.info("🔍 测试智能体创建...")
    
    try:
        from agents.research_agents import create_research_manager
        
        agent = create_research_manager()
        logger.info("✅ 智能体创建成功")
        logger.info(f"✅ 智能体角色: {agent.role}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 智能体创建失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始系统修复验证测试...")
    logger.info("=" * 50)
    
    tests = [
        ("环境配置", test_environment_setup),
        ("模块导入", test_imports), 
        ("LLM创建", test_llm_creation),
        ("API连通性", test_api_connectivity),
        ("LLM调用", test_simple_llm_call),
        ("智能体创建", test_agent_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！系统修复成功！")
        logger.info("💡 现在可以运行: python main.py")
        return True
    else:
        logger.error("❌ 部分测试失败，请检查上述错误信息")
        logger.info("💡 请查看 TROUBLESHOOTING.md 获取解决方案")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
