#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页爬虫工具 - 主程序入口
"""
import sys
import os

# 判断是否为PyInstaller打包环境
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)

# 确保工作目录正确
os.chdir(BASE_DIR)

# 创建必要的目录
for dir_path in ['data/tasks', 'data/output', 'config']:
    full_path = os.path.join(BASE_DIR, dir_path)
    os.makedirs(full_path, exist_ok=True)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.gui.launcher import LauncherWindow
from src.gui.simple_mode import SimpleModeWindow
from src.gui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("网页爬虫工具")
    app.setApplicationVersion("1.0.0")
    
    # 设置点击关闭按钮时自动退出程序
    app.setQuitOnLastWindowClosed(True)
    
    # 显示启动器选择模式
    launcher = LauncherWindow()
    launcher.show()
    
    # 等待用户选择
    app.exec()
    
    # 根据选择启动对应窗口
    if launcher.selected_mode == "simple":
        # 简单模式
        window = SimpleModeWindow()
        
        def switch_to_advanced():
            window.close()
            advanced_window = MainWindow()
            advanced_window.show()
            app.exec()
        
        window.switch_to_advanced.connect(switch_to_advanced)
        window.show()
        app.exec()
        
    elif launcher.selected_mode == "advanced":
        # 高级模式
        window = MainWindow()
        window.show()
        app.exec()


if __name__ == "__main__":
    main()