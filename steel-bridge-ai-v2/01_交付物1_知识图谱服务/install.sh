#!/bin/bash
# 安装脚本：设置柳林桥知识图谱服务

echo "🏗️ 柳林桥知识图谱服务 - 安装脚本"
echo "===================================="

# 检查Python版本
python3 --version || { echo "❌ 需要Python 3.8+"; exit 1; }

# 创建虚拟环境（推荐）
echo ""
echo "📦 创建虚拟环境..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ 基础依赖安装完成"
echo ""

# 检查ODA File Converter
echo "🔍 检查ODA File Converter..."
if command -v odafileconverter &> /dev/null; then
    echo "✅ ODA File Converter已安装"
else
    echo "⚠️  ODA File Converter未安装"
    echo ""
    echo "图纸尺寸解析功能需要此工具。安装方式："
    echo ""
    echo "【Linux】"
    echo "1. 访问 https://www.opendesign.com/guestfiles/oda_file_converter"
    echo "2. 下载 Linux 版本"
    echo "3. 解压并运行 ./install.sh"
    echo ""
    echo "【Docker】（最简单）"
    echo "docker pull opendesign/odafileconverter"
    echo ""
    echo "安装后重新运行此脚本"
fi

echo ""
echo "===================================="
echo "安装完成！"
echo ""
echo "启动服务："
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "或一键启动（整个项目）："
echo "  cd .. && ./start.sh"
