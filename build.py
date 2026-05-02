# -*- coding: utf-8 -*-
"""
网页爬虫工具 - EXE打包脚本
将Python程序打包成独立的EXE可执行文件
"""

import PyInstaller.__main__
import os
import sys
import shutil

# ========== 项目配置 ==========
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_DIR, 'spider_tool.spec')

# 打包配置
APP_NAME = '网页爬虫工具'  # 应用名称
VERSION = '1.0.0'


def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = os.path.join(PROJECT_DIR, dir_name)
        if os.path.exists(dir_path):
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)


def copy_runtime_files(dist_dir):
    """复制运行时需要的文件到发布目录"""
    # 创建数据存储目录
    data_dir = os.path.join(dist_dir, 'data')
    os.makedirs(os.path.join(data_dir, 'tasks'), exist_ok=True)   # 任务配置目录
    os.makedirs(os.path.join(data_dir, 'output'), exist_ok=True)  # 输出文件目录
    
    # 复制说明文档
    readme_src = os.path.join(PROJECT_DIR, 'README.md')
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, dist_dir)
    
    print("运行时文件复制完成")


def create_launcher(dist_dir):
    """创建启动批处理文件"""
    # 批处理内容：设置UTF-8编码，启动EXE
    launcher_content = '@echo off\r\nchcp 65001 >nul\r\ntitle 网页爬虫工具\r\ncd /d "%~dp0"\r\nstart "" "网页爬虫工具.exe"\r\n'
    
    # 使用UTF-8 BOM编码写入（确保中文正常显示）
    launcher_path = os.path.join(dist_dir, '启动爬虫工具.bat')
    with open(launcher_path, 'w', encoding='utf-8-sig') as f:
        f.write(launcher_content)
    
    print(f"启动脚本已创建: {launcher_path}")


def main():
    """主函数 - 执行打包流程"""
    print("=" * 60)
    print(f"  网页爬虫工具 v{VERSION} - EXE打包工具")
    print("=" * 60)
    print()
    
    # 检查spec配置文件是否存在
    if not os.path.exists(SPEC_FILE):
        print(f"[错误] 找不到配置文件: {SPEC_FILE}")
        return 1
    
    # 步骤1：清理旧的构建文件
    print("[1/4] 清理构建目录...")
    clean_build_dirs()
    
    # 步骤2：运行PyInstaller打包
    print("[2/4] 开始打包（需要5-10分钟）...")
    print()
    
    try:
        PyInstaller.__main__.run([
            '--clean',       # 清理临时文件
            '--noconfirm',   # 不确认覆盖
            SPEC_FILE        # 使用spec配置文件
        ])
    except Exception as e:
        print(f"[错误] 打包失败: {e}")
        return 1
    
    # 步骤3：复制运行时文件
    print("[3/4] 复制运行时文件...")
    dist_dir = os.path.join(PROJECT_DIR, 'dist', APP_NAME)
    if os.path.exists(dist_dir):
        copy_runtime_files(dist_dir)
        create_launcher(dist_dir)
    
    # 步骤4：清理构建临时文件
    print("[4/4] 清理临时文件...")
    build_dir = os.path.join(PROJECT_DIR, 'build')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    # 打包完成提示
    print()
    print("=" * 60)
    print("  打包完成！")
    print("=" * 60)
    print()
    print(f"输出目录: dist\\{APP_NAME}")
    print(f"可执行文件: dist\\{APP_NAME}\\{APP_NAME}.exe")
    print()
    print("使用说明:")
    print("1. 将 dist 目录下的整个文件夹复制到目标机器")
    print("2. 双击「启动爬虫工具.bat」或「网页爬虫工具.exe」运行")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())