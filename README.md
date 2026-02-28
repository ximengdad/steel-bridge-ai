# 钢箱梁智能助手 - 一航局课题交付包

## 项目简介
面向AI的模型驱动下钢箱梁模块化设计与生产数据架构研究

## 两项核心交付物
1. **基于Web端的人工智能知识图谱**（系统数据架构大模型）
2. **基于Web端的钢箱梁大语言模型**（工程建议生成系统）

## 快速启动

### 本地运行
```bash
# 交付物1：知识图谱服务
cd 01_交付物1_知识图谱服务
pip install -r requirements.txt
python init_data.py
python main.py
# 访问 http://localhost:8000

# 交付物2：大模型服务
cd 02_交付物2_Web端大模型/backend
pip install -r requirements.txt
export OPENAI_API_KEY=你的密钥
python run.py
# 访问 http://localhost:8081
```

### GitHub Codespaces 一键运行
点击上方 "Code" → "Codespaces" → "Create codespace on main"

然后在终端运行：
```bash
# 启动知识图谱服务
cd 01_交付物1_知识图谱服务 && python3 init_data.py && python3 main.py &

# 启动大模型服务
cd 02_交付物2_Web端大模型/backend && python3 run.py
```

## 技术栈
- 后端：FastAPI + Python
- 前端：HTML + JavaScript
- 数据：JSON-LD 语义网格式
- 大模型：OpenAI API / 本地模型

## 课题要求对照
| 合同要求 | 实现方式 |
|---------|---------|
| 基于Web端的人工智能知识图谱 | FastAPI提供HTTP接口 |
| 导出知识图谱文件 | `/kg/export`接口 |
| 基于Web端的大语言模型 | FastAPI + 前端HTML |
| 四阶段支持 | 设计/生产/质检/装配 Agent |

## 许可证
MIT
