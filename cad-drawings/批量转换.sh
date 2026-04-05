#!/bin/bash
# 柳林桥DWG批量转换脚本（Linux/Mac）

echo "=========================================="
echo "柳林桥DWG批量转换脚本"
echo "=========================================="
echo ""

# 设置路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_DIR="${SCRIPT_DIR}/柳林桥CAD图纸"
OUTPUT_DIR="${SCRIPT_DIR}/柳林桥DXF图纸"

# 检查ODA File Converter
if command -v ODAFileConverter > /dev/null 2>&1; then
    ODA_CMD="ODAFileConverter"
elif [ -f "/usr/bin/ODAFileConverter" ]; then
    ODA_CMD="/usr/bin/ODAFileConverter"
elif [ -f "/opt/ODAFileConverter/ODAFileConverter.AppImage" ]; then
    ODA_CMD="/opt/ODAFileConverter/ODAFileConverter.AppImage"
else
    echo "❌ 错误：找不到ODA File Converter"
    echo ""
    echo "请按以下步骤安装："
    echo "1. 访问 https://www.opendesign.com/guestfiles/oda_file_converter"
    echo "2. 下载 Linux 版本（AppImage推荐）"
    echo "3. chmod +x ODAFileConverter.AppImage"
    echo "4. 将路径添加到系统PATH，或修改本脚本的ODA_CMD变量"
    echo ""
    read -p "按Enter键退出..."
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "开始转换..."
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "ODA路径: $ODA_CMD"
echo ""

# 执行转换
"$ODA_CMD" "$INPUT_DIR" "$OUTPUT_DIR" "ACAD2018" "DXF" "1" "1"

echo ""
echo "=========================================="
echo "转换完成！"
echo "输出目录: $OUTPUT_DIR"
echo "=========================================="
read -p "按Enter键退出..."
