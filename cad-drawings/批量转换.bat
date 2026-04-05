@echo off
chcp 65001
echo ==========================================
echo 柳林桥DWG批量转换脚本
echo ==========================================
echo.

REM 设置路径（根据实际情况修改）
set "ODA_PATH=C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
set "INPUT_DIR=%~dp0柳林桥CAD图纸"
set "OUTPUT_DIR=%~dp0柳林桥DXF图纸"

REM 检查ODA是否存在
if not exist "%ODA_PATH%" (
    echo ❌ 错误：找不到ODA File Converter
    echo 请修改脚本中的ODA_PATH为你的安装路径
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 开始转换...
echo 输入目录: %INPUT_DIR%
echo 输出目录: %OUTPUT_DIR%
echo.

REM 执行批量转换
"%ODA_PATH%" "%INPUT_DIR%" "%OUTPUT_DIR%" "ACAD2018" "DXF" "1" "1"

echo.
echo ==========================================
echo 转换完成！
echo 输出目录: %OUTPUT_DIR%
echo ==========================================
pause
