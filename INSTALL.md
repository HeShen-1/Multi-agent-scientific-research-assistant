# 安装指南

本指南将帮助您完成多智能体科研助手的安装和配置。

## 环境要求

- Python 3.8 或更高版本
- `pip` 包管理器
- Git 版本控制工具

## 安装步骤

### 方法一：一键安装（推荐）

如果您希望快速完成所有配置，项目根目录下的 `quick_start.py` 脚本可以自动完成所有步骤。

```bash
python quick_start.py
```

该脚本会自动执行以下操作：
1.  检查Python环境。
2.  安装所有必需的依赖包。
3.  从 `env_example.txt` 创建 `.env` 配置文件。
4.  提示您输入API密钥并自动保存。
5.  运行连接测试以确保配置正确。

### 方法二：手动安装

如果您希望手动控制安装过程，请按照以下步骤操作。

#### 1. 克隆项目（如果尚未下载）

```bash
git clone <your-repository-url>
cd Multi-AgentResearchAssistant
```

#### 2. 安装依赖

项目的所有依赖都列在 `requirements.txt` 文件中。

```bash
pip install -r requirements.txt
```

#### 3. 配置API密钥

API密钥和模型配置存储在 `.env` 文件中。

首先，从模板文件复制一份配置文件：
```bash
cp env_example.txt .env
```

然后，使用您喜欢的文本编辑器打开 `.env` 文件，并填入您的API密钥。

```ini
# .env

# 必需的API密钥
OPENAI_API_KEY="sk-..."  # 填入您的DeepSeek API密钥
TAVILY_API_KEY="tvly-..." # 填入您的Tavily Search API密钥

# API端点配置
OPENAI_API_BASE="https://api.deepseek.com"

# 模型配置 (通常无需修改)
OPENAI_MODEL_NAME="deepseek-chat"
OPENAI_TEMPERATURE=0.7

# 搜索配置 (可选)
MAX_SEARCH_RESULTS=5
```

**如何获取API密钥？**

- **DeepSeek API**:
    1.  访问 [DeepSeek开放平台](https://platform.deepseek.com/)。
    2.  注册并登录您的账户。
    3.  在API密钥管理页面创建一个新的密钥。

- **Tavily Search API**:
    1.  访问 [Tavily AI](https://tavily.com/)。
    2.  注册并登录您的账户。
    3.  在仪表板中找到您的API密钥。


## 运行系统

完成安装和配置后，您可以根据需要选择以下任一模式运行本系统。

### 命令行模式

直接在终端中与智能体进行交互。

```bash
# 启动后，程序会提示您输入研究主题
python main.py

# 或者，直接将研究主题作为参数传入
python main.py "AI在药物研发领域的最新进展"
```

### Web界面模式

通过浏览器使用图形化界面。

```bash
streamlit run app.py
```
执行命令后，终端会显示一个本地网址（通常是 `http://localhost:8501`），在浏览器中打开即可。

## 系统测试

为确保所有配置都正确无误，您可以运行项目中的测试脚本。

```bash
# 运行配置和API连接测试
python test_openai_integration.py
```

如果所有测试都通过，说明您的环境已准备就绪。如果遇到问题，请参考 `解决方案.md` 文档。
