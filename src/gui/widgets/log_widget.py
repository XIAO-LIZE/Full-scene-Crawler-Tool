"""
日志显示小部件
"""
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont


class LogWidget(QWidget):
    """日志显示小部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("保存日志")
        save_btn.clicked.connect(self.save_log)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_text)
    
    def append_log(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建文本格式
        format = QTextCharFormat()
        
        if level == "ERROR":
            format.setForeground(QColor("red"))
        elif level == "WARNING":
            format.setForeground(QColor("orange"))
        elif level == "SUCCESS":
            format.setForeground(QColor("green"))
        else:
            format.setForeground(QColor("black"))
        
        # 添加日志
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        cursor.insertText(f"[{timestamp}] [{level}] ", format)
        cursor.insertText(f"{message}\n")
        
        # 滚动到底部
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def save_log(self):
        """保存日志"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "spider_log.txt", "文本文件 (*.txt)"
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())