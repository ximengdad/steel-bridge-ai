#!/bin/bash

echo "🏗️ 柳林桥钢箱梁智能助手 - 启动脚本"
echo "===================================="

# 设置基础路径
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
KG_SERVICE_DIR="$BASE_DIR/01_交付物1_知识图谱服务"
LLM_SERVICE_DIR="$BASE_DIR/02_交付物2_Web端大模型/backend"
FRONTEND_DIR="$BASE_DIR/02_交付物2_Web端大模型/frontend"

echo ""
echo "📁 项目路径: $BASE_DIR"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 启动知识图谱服务
echo "🚀 启动知识图谱服务 (端口 8000)..."
cd "$KG_SERVICE_DIR"

# 检查依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 安装知识图谱服务依赖..."
    pip install -r requirements.txt -q
fi

# 启动服务（后台）
python3 main.py &
KG_PID=$!
echo "   知识图谱服务 PID: $KG_PID"
echo "   接口文档: http://localhost:8000/docs"
echo ""

# 等待知识图谱服务启动
sleep 2

# 启动大模型服务
echo "🚀 启动大模型服务 (端口 8081)..."
cd "$LLM_SERVICE_DIR"

# 检查依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 安装大模型服务依赖..."
    pip install -r requirements.txt -q
fi

# 启动服务（后台）
python3 run.py &
LLM_PID=$!
echo "   大模型服务 PID: $LLM_PID"
echo "   接口文档: http://localhost:8081/docs"
echo ""

# 等待服务启动
sleep 2

echo "===================================="
echo "✅ 服务启动完成！"
echo ""
echo "📊 访问地址:"
echo "   • 前端界面: file://$FRONTEND_DIR/index.html"
echo "   • 知识图谱API: http://localhost:8000"
echo "   • 大模型API: http://localhost:8081"
echo ""
echo "🔧 常用接口:"
echo "   • 项目信息: http://localhost:8000/project/info"
echo "   • 图纸搜索: http://localhost:8000/drawings/search?keyword=拱肋"
echo "   • 草图生成: http://localhost:8000/sketch/generate?sketch_type=arch_installation"
echo ""
echo "⚠️  按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $KG_PID $LLM_PID; echo ''; echo '🛑 服务已停止'; exit 0" INT
wait
