@echo off
chcp 65001 >nul
title 全场景爬虫工具 - 打包

echo.
echo  ╔════════════════════════════════════════════════════════════╗
echo  ║              全场景爬虫工具 v1.0                          ║
echo  ║              EXE打包工具                                  ║
echo  ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/5] 检查Python环境...
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)
echo Python已就绪
echo.

echo [2/5] 配置虚拟环境...
if not exist "venv\Scripts\python.exe" (
    echo 正在创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo.

echo [3/5] 安装依赖包...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo [4/5] 准备资源文件...
if not exist "assets" mkdir "assets"
echo.

echo [5/5] 开始打包...
echo 打包过程需要5-10分钟，请耐心等待...
echo.

python build.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo 打包完成！
echo 输出目录: dist\UniversalSpiderTool\
echo.
pause