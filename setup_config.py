#!/usr/bin/env python3
"""
多智能体科研助手配置助手
Configuration Helper for Multi-Agent Research Assistant

这个脚本帮助用户快速配置系统环境变量
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """设置环境配置"""
    print("🤖 多智能体科研助手配置助手")
    print("=" * 50)
    
    # 检查是否存在.env文件
    if os.path.exists('.env'):
        print("✅ 发现现有的.env配置文件")
        choice = input("是否要重新配置？(y/n): ").strip().lower()
        if choice not in ['y', 'yes', '是']:
            print("配置已取消")
            return
    
    # 复制示例文件
    if os.path.exists('env_example.txt'):
        try:
            shutil.copy2('env_example.txt', '.env')
            print("✅ 已创建.env配置文件")
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return
    else:
        print("❌ 未找到env_example.txt文件")
        return
    
    print("\n📝 请按照以下步骤完成配置：")
    print("1. 获取DeepSeek API密钥：")
    print("   - 访问 https://platform.deepseek.com/")
    print("   - 注册账号并获取API密钥")
    print("   - 密钥格式通常为: sk-xxxxxxxxxxxxxxxx")
    
    print("\n2. 编辑.env文件：")
    print("   - 用文本编辑器打开.env文件")
    print("   - 将OPENAI_API_KEY的值替换为您的真实API密钥")
    print("   - 保存文件")
    
    print("\n3. 可选配置：")
    print("   - 如需要更强的搜索能力，可配置Tavily API密钥")
    print("   - 访问 https://tavily.com/ 获取API密钥")
    
    # 尝试自动配置API密钥
    print("\n" + "=" * 50)
    auto_config = input("是否现在输入API密钥进行自动配置？(y/n): ").strip().lower()
    
    if auto_config in ['y', 'yes', '是']:
        api_key = input("请输入您的DeepSeek API密钥: ").strip()
        if api_key and api_key.startswith('sk-'):
            try:
                # 读取.env文件内容
                with open('.env', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换API密钥
                content = content.replace('sk-your-deepseek-api-key-here', api_key)
                
                # 确保API_BASE正确
                if 'OPENAI_API_BASE="https://www.deepseek.com/"' in content:
                    content = content.replace('OPENAI_API_BASE="https://www.deepseek.com/"', 'OPENAI_API_BASE="https://api.deepseek.com/v1"')
                elif 'OPENAI_API_BASE="https://api.deepseek.com"' in content:
                    content = content.replace('OPENAI_API_BASE="https://api.deepseek.com"', 'OPENAI_API_BASE="https://api.deepseek.com/v1"')
                
                # 写回文件
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ API密钥配置成功！")
                
                # 可选配置Tavily
                tavily_choice = input("是否配置Tavily搜索API密钥？(y/n): ").strip().lower()
                if tavily_choice in ['y', 'yes', '是']:
                    tavily_key = input("请输入Tavily API密钥: ").strip()
                    if tavily_key and tavily_key.startswith('tvly-'):
                        content = content.replace('tvly-your-tavily-api-key-here', tavily_key)
                        with open('.env', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("✅ Tavily API密钥配置成功！")
                
            except Exception as e:
                print(f"❌ 自动配置失败: {e}")
                print("请手动编辑.env文件")
        else:
            print("❌ 无效的API密钥格式")
            print("请手动编辑.env文件")
    
    print("\n🎉 配置完成！")
    print("现在可以运行以下命令启动系统：")
    print("python main.py")

def verify_config():
    """验证配置是否正确"""
    print("\n🔍 验证配置...")
    
    if not os.path.exists('.env'):
        print("❌ .env文件不存在")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'sk-your-deepseek-api-key-here':
        print("❌ DeepSeek API密钥未配置")
        return False
    
    print("✅ 基本配置验证通过")
    
    # 测试API连接
    try:
        from openai import OpenAI
        
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'deepseek-chat')
        
        # 确保base_url格式正确（不包含/v1，OpenAI SDK会自动添加）
        if api_base.endswith('/v1'):
            api_base = api_base[:-3]
        
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 发送测试请求
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False,
            max_tokens=100
        )
        
        print(f"✅ API连接测试成功: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        print("请检查API密钥和网络连接")
        return False

if __name__ == "__main__":
    setup_environment()
    verify_config()
