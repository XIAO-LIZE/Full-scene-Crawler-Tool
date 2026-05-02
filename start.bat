@echo off
chcp 65001 >nul 2>&1
title 网页爬虫工具

echo.
echo  ========================================
echo        全场景爬虫工具 v1.0
echo  ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %cd%
echo.

echo [1/4] 检查Python环境...
python --version 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未找到Python！
    echo 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo Python检查通过
echo.

echo [2/4] 配置虚拟环境...
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [错误] 创建虚拟环境失败！
        echo.
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
) else (
    echo 虚拟环境已存在
)

if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [错误] 虚拟环境文件不完整！
    echo 请删除venv文件夹后重新运行
    echo.
    pause
    exit /b 1
)
echo 虚拟环境检查通过
echo.

echo [3/4] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo [错误] 激活虚拟环境失败！
    echo.
    pause
    exit /b 1
)
echo 虚拟环境已激活

echo 检查依赖包...
python -c "import PySide6; print('PySide6:', PySide6.__version__)" 2>&1
if errorlevel 1 (
    echo.
    echo 正在安装依赖包，请稍候...
    echo 这可能需要几分钟时间...
    echo.
    python -m pip install --upgrade pip -q
    echo 使用阿里云镜像安装...
    python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if errorlevel 1 (
        echo.
        echo [警告] 镜像安装失败，尝试默认源...
        python -m pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo [错误] 依赖安装失败！请检查网络连接
            echo.
            pause
            exit /b 1
        )
    )
    echo 依赖安装完成
) else (
    echo 依赖包已安装
)
echo.

echo [4/4] 启动程序...
echo ========================================
echo.
python main.py
set APP_EXIT_CODE=%errorlevel%

echo.
echo ========================================
if %APP_EXIT_CODE% neq 0 (
    echo 程序异常退出，错误代码: %APP_EXIT_CODE%
) else (
    echo 程序正常退出
)
echo.
pause
exit /b %APP_EXIT_CODE%