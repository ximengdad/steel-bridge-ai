#!/bin/bash

echo "🚀 启动钢箱梁智能助手..."

# 启动知识图谱服务
cd 01_交付物1_知识图谱服务
python3 init_data.py
python3 main.py &
KG_PID=$!
echo "✅ 知识图谱服务已启动 (PID: $KG_PID)"

# 等待知识图谱服务启动
sleep 3

# 启动大模型服务
cd ../02_交付物2_Web端大模型/backend
python3 run.py &
LLM_PID=$!
echo "✅ 大模型服务已启动 (PID: $LLM_PID)"

echo ""
echo "📍 访问地址:"
echo "  - 知识图谱API: http://localhost:8000"
echo "  - 大模型API:   http://localhost:8081"
echo "  - API文档:     http://localhost:8000/docs"
echo ""
echo "🛑 停止服务: kill $KG_PID $LLM_PID"
