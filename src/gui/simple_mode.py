# -*- coding: utf-8 -*-
"""
简单模式界面 - 一键爬取
"""

import json
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QGroupBox, QProgressBar, QFileDialog, QMessageBox,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor


class SpiderThread(QThread):
    """爬虫线程"""
    progress = Signal(str, int)
    finished = Signal(bool, str)
    error = Signal(str)
    
    def __init__(self, url, extract_type, save_path):
        super().__init__()
        self.url = url
        self.extract_type = extract_type
        self.save_path = save_path
    
    def run(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            self.progress.emit("正在连接...", 10)
            
            if self.extract_type == "api":
                resp = requests.get(self.url, headers=headers, timeout=30)
                data = resp.json()
                self.progress.emit("解析数据...", 60)
                with open(self.save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                resp = requests.get(self.url, headers=headers, timeout=30)
                resp.encoding = resp.apparent_encoding
                soup = BeautifulSoup(resp.text, 'lxml')
                self.progress.emit("解析页面...", 40)
                
                if self.extract_type == "text":
                    results = [{'type': t.name, 'text': t.get_text(strip=True)} 
                              for t in soup.find_all(['p','h1','h2','h3','li']) 
                              if t.get_text(strip=True) and len(t.get_text(strip=True)) > 2]
                elif self.extract_type == "links":
                    results = [{'text': a.get_text(strip=True) or '(无文字)', 'url': a['href']} 
                              for a in soup.find_all('a', href=True) 
                              if a['href'].startswith(('http://','https://','/'))]
                elif self.extract_type == "images":
                    results = [{'alt': img.get('alt',''), 'src': img['src']} 
                              for img in soup.find_all('img', src=True)]
                elif self.extract_type == "table":
                    results = []
                    for table in soup.find_all('table'):
                        rows = [[td.get_text(strip=True) for td in tr.find_all(['td','th'])] 
                               for tr in table.find_all('tr')]
                        rows = [r for r in rows if r]
                        if rows:
                            results.append(rows)
                else:
                    results = {
                        'title': soup.title.string.strip() if soup.title and soup.title.string else '',
                        'text': soup.get_text(strip=True)[:5000],
                        'links_count': len(soup.find_all('a')),
                        'images_count': len(soup.find_all('img'))
                    }
                
                self.progress.emit("保存数据...", 80)
                with open(self.save_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.progress.emit("完成！", 100)
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.error.emit(str(e))


class SimpleModeWindow(QMainWindow):
    """简单模式窗口"""
    switch_to_advanced = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.current_path = ""
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("网页爬虫工具 - 简单模式")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("background: #F0F2F5;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.setCentralWidget(scroll)
        
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setSpacing(18)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # ========== 标题 ==========
        header = QFrame()
        header.setStyleSheet("background: #4A5AEF; border-radius: 14px;")
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(20, 22, 20, 22)
        
        title = QLabel("网页数据抓取")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent; border: none;")
        header_layout.addWidget(title)
        
        sub = QLabel("输入网址 → 选择内容 → 一键抓取")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; background: transparent; border: none;")
        header_layout.addWidget(sub)
        layout.addWidget(header)
        
        # ========== 第1步 ==========
        g1 = QGroupBox("第1步：输入网址")
        g1.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 12px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background: white;
            }
        """)
        g1_layout = QVBoxLayout(g1)
        g1_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入网址，例如：https://www.example.com")
        self.url_input.setMinimumHeight(46)
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #B0B8C4;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background: white;
                color: #1A1A1A;
            }
            QLineEdit:focus {
                border-color: #4A5AEF;
            }
        """)
        g1_layout.addWidget(self.url_input)
        
        hint = QLabel("支持 http:// 和 https:// 协议")
        hint.setStyleSheet("color: #555555; font-size: 12px; background: transparent; border: none;")
        g1_layout.addWidget(hint)
        layout.addWidget(g1)
        
        # ========== 第2步 ==========
        g2 = QGroupBox("第2步：选择提取内容")
        g2.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 12px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background: white;
            }
        """)
        g2_layout = QVBoxLayout(g2)
        g2_layout.setSpacing(10)
        
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(46)
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #B0B8C4;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background: white;
                color: #1A1A1A;
            }
            QComboBox:focus {
                border-color: #4A5AEF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                selection-background-color: #4A5AEF;
                selection-color: white;
            }
        """)
        self.type_combo.addItems([
            "自动识别 - 智能提取主要内容",
            "全部文本 - 提取所有文字",
            "所有链接 - 提取页面链接",
            "所有图片 - 提取图片地址",
            "表格数据 - 提取表格内容",
            "API数据 - 获取JSON接口"
        ])
        g2_layout.addWidget(self.type_combo)
        
        self.hint_label = QLabel("大多数网站选择「自动识别」即可")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #555555; font-size: 12px; background: transparent; border: none;")
        g2_layout.addWidget(self.hint_label)
        layout.addWidget(g2)
        
        # ========== 第3步 ==========
        g3 = QGroupBox("第3步：选择保存位置")
        g3.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 12px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background: white;
            }
        """)
        g3_layout = QVBoxLayout(g3)
        g3_layout.setSpacing(10)
        
        save_row = QHBoxLayout()
        save_row.setSpacing(10)
        
        self.path_input = QLineEdit()
        self.path_input.setMinimumHeight(46)
        self.path_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #B0B8C4;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background: white;
                color: #1A1A1A;
            }
            QLineEdit:focus {
                border-color: #4A5AEF;
            }
        """)
        self.path_input.setText(os.path.join(os.path.expanduser("~"), "Desktop", "爬取结果.json"))
        
        browse_btn = QPushButton("浏览")
        browse_btn.setFixedSize(80, 46)
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #555555;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #333333;
            }
        """)
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.clicked.connect(self._browse)
        
        save_row.addWidget(self.path_input)
        save_row.addWidget(browse_btn)
        g3_layout.addLayout(save_row)
        layout.addWidget(g3)
        
        # ========== 按钮 ==========
        btn_row = QHBoxLayout()
        btn_row.setSpacing(18)
        
        self.start_btn = QPushButton("开始爬取")
        self.start_btn.setMinimumHeight(55)
        self.start_btn.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #4A5AEF;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3A4AD0;
            }
            QPushButton:disabled {
                background: #D0D5DD;
                color: #999;
            }
        """)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._start)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumHeight(55)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #DC3545;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 16px 28px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #C82333;
            }
            QPushButton:disabled {
                background: #D0D5DD;
                color: #999;
            }
        """)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        
        btn_row.addWidget(self.start_btn, 3)
        btn_row.addWidget(self.stop_btn, 1)
        layout.addLayout(btn_row)
        
        # ========== 进度 ==========
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                text-align: center;
                background: #D0D5DD;
                height: 20px;
                font-size: 11px;
                font-weight: bold;
                color: #1A1A1A;
            }
            QProgressBar::chunk {
                background: #4A5AEF;
                border-radius: 10px;
            }
        """)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px; background: transparent; border: none; color: #1A1A1A;")
        layout.addWidget(self.status)
        
        # ========== 结果 ==========
        g4 = QGroupBox("结果预览")
        g4.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 12px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background: white;
            }
        """)
        g4_layout = QVBoxLayout(g4)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 11))
        self.result_text.setMaximumHeight(130)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: #F5F5F5;
                border: 2px solid #D0D5DD;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, monospace;
                font-size: 12px;
                color: #1A1A1A;
            }
        """)
        g4_layout.addWidget(self.result_text)
        layout.addWidget(g4)
        
        # ========== 底部 ==========
        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        
        btn1 = QPushButton("打开目录")
        btn1.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #4A5AEF;
                color: #4A5AEF;
            }
        """)
        btn1.setCursor(Qt.PointingHandCursor)
        btn1.clicked.connect(self._open_dir)
        
        btn2 = QPushButton("打开文件")
        btn2.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1A1A1A;
                border: 2px solid #D0D5DD;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #4A5AEF;
                color: #4A5AEF;
            }
        """)
        btn2.setCursor(Qt.PointingHandCursor)
        btn2.clicked.connect(self._open_file)
        
        bottom.addWidget(btn1)
        bottom.addWidget(btn2)
        bottom.addStretch()
        
        adv_btn = QPushButton("高级模式 →")
        adv_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4A5AEF;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #3A4AD0;
            }
        """)
        adv_btn.setCursor(Qt.PointingHandCursor)
        adv_btn.clicked.connect(lambda: self.switch_to_advanced.emit())
        bottom.addWidget(adv_btn)
        
        layout.addLayout(bottom)
        
        self.type_combo.currentIndexChanged.connect(self._update_hint)
    
    def _update_hint(self, idx):
        hints = [
            "大多数网站选择「自动识别」即可",
            "提取页面所有文字内容",
            "提取页面中所有链接地址",
            "提取页面中所有图片地址",
            "提取页面中的表格数据",
            "适用于返回JSON的API接口"
        ]
        if 0 <= idx < len(hints):
            self.hint_label.setText(hints[idx])
    
    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存位置", self.path_input.text(), "JSON (*.json)")
        if path:
            self.path_input.setText(path)
    
    def _start(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入网址")
            return
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "提示", "请选择保存位置")
            return
        
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        types = ["auto", "text", "links", "images", "table", "api"]
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status.setText("正在准备...")
        self.status.setStyleSheet("color: #17A2B8; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        self.result_text.clear()
        
        self.current_path = path
        self.thread = SpiderThread(url, types[self.type_combo.currentIndex()], path)
        self.thread.progress.connect(self._on_progress)
        self.thread.finished.connect(self._on_finished)
        self.thread.error.connect(self._on_error)
        self.thread.start()
    
    def _stop(self):
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self._reset()
            self.status.setText("已停止")
            self.status.setStyleSheet("color: #FFC107; font-size: 14px; font-weight: bold; background: transparent; border: none;")
    
    def _on_progress(self, msg, val):
        self.status.setText(msg)
        self.progress.setValue(val)
    
    def _on_finished(self, ok, path):
        self._reset()
        if ok:
            self.progress.setValue(100)
            self.status.setText("爬取完成！")
            self.status.setStyleSheet("color: #28A745; font-size: 16px; font-weight: bold; background: transparent; border: none;")
            self._preview(path)
            QMessageBox.information(self, "成功", f"数据已保存到:\n{path}")
        else:
            self.status.setText("爬取失败")
            self.status.setStyleSheet("color: #DC3545; font-size: 14px; font-weight: bold; background: transparent; border: none;")
    
    def _on_error(self, msg):
        self._reset()
        self.status.setText("出错了")
        self.status.setStyleSheet("color: #DC3545; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        self.result_text.setText(f"错误: {msg}")
        QMessageBox.critical(self, "错误", f"爬取失败:\n{msg}")
    
    def _preview(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                txt = f"共 {len(data)} 条\n{'─'*30}\n"
                for i, item in enumerate(data[:5]):
                    s = json.dumps(item, ensure_ascii=False)
                    txt += f"[{i+1}] {s[:100]}{'...' if len(s)>100 else ''}\n"
                if len(data) > 5:
                    txt += f"\n... 还有 {len(data)-5} 条"
            else:
                txt = json.dumps(data, ensure_ascii=False, indent=2)[:600]
            self.result_text.setText(txt)
        except:
            self.result_text.setText(f"已保存: {path}")
    
    def _reset(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setVisible(False)
    
    def _open_dir(self):
        p = self.path_input.text()
        if p and os.path.exists(os.path.dirname(p)):
            os.startfile(os.path.dirname(p))
    
    def _open_file(self):
        if self.current_path and os.path.exists(self.current_path):
            os.startfile(self.current_path)
        else:
            QMessageBox.information(self, "提示", "请先执行爬取")
    
    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
        event.accept()