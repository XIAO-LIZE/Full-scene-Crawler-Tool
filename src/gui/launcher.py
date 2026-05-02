# -*- coding: utf-8 -*-
"""
启动器模块 - 模式选择界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


class ModeCard(QFrame):
    """模式选择卡片"""
    clicked = Signal()
    
    def __init__(self, title, desc, color, tag_text, parent=None):
        super().__init__(parent)
        self.color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(200, 260)
        self.setStyleSheet(f"""
            ModeCard {{
                background: white;
                border: 2px solid #D0D5DD;
                border-radius: 16px;
            }}
            ModeCard:hover {{
                border: 2px solid {color};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # 图标圆
        icon = QLabel()
        icon.setFixedSize(64, 64)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"""
            background: {color};
            border-radius: 32px;
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        if "简单" in title:
            icon.setText("简")
        else:
            icon.setText("专")
        layout.addWidget(icon, alignment=Qt.AlignCenter)
        
        # 标题 - 黑色
        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        t.setStyleSheet("color: #1A1A1A; background: transparent; border: none;")
        layout.addWidget(t)
        
        # 描述 - 深灰
        d = QLabel(desc)
        d.setAlignment(Qt.AlignCenter)
        d.setWordWrap(True)
        d.setStyleSheet("color: #333333; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(d)
        
        # 标签
        tag = QLabel(tag_text)
        tag.setAlignment(Qt.AlignCenter)
        tag.setFixedSize(60, 24)
        tag.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(tag, alignment=Qt.AlignCenter)
    
    def enterEvent(self, event):
        self.setStyleSheet(f"ModeCard {{ background: white; border: 2px solid {self.color}; border-radius: 16px; }}")
    
    def leaveEvent(self, event):
        self.setStyleSheet("ModeCard { background: white; border: 2px solid #D0D5DD; border-radius: 16px; }")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class LauncherWindow(QWidget):
    """启动器窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("网页爬虫工具")
        self.setFixedSize(520, 540)
        self.setStyleSheet("background: #F0F2F5;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 25, 40, 25)
        
        # ========== Logo ==========
        logo = QLabel("SP")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(70, 70)
        logo.setStyleSheet("""
            background: #4A5AEF;
            color: white;
            font-size: 26px;
            font-weight: bold;
            border-radius: 35px;
        """)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        
        # 标题 - 黑色
        title = QLabel("网页爬虫工具")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setStyleSheet("color: #1A1A1A; background: transparent; border: none;")
        layout.addWidget(title)
        
        # 副标题 - 深灰
        sub = QLabel("简单高效的数据采集助手")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #555555; font-size: 14px; background: transparent; border: none;")
        layout.addWidget(sub)
        
        layout.addSpacing(15)
        
        # ========== 卡片 ==========
        cards = QHBoxLayout()
        cards.setSpacing(25)
        cards.setAlignment(Qt.AlignCenter)
        
        simple = ModeCard(
            title="简单模式",
            desc="适合新手用户\n只需输入网址\n一键快速抓取",
            color="#00B894",
            tag_text="推荐"
        )
        simple.clicked.connect(lambda: self._select("simple"))
        cards.addWidget(simple)
        
        advanced = ModeCard(
            title="高级模式",
            desc="适合专业用户\n自定义规则配置\n多种数据源支持",
            color="#4A5AEF",
            tag_text="专业"
        )
        advanced.clicked.connect(lambda: self._select("advanced"))
        cards.addWidget(advanced)
        
        layout.addLayout(cards)
        
        layout.addStretch()
        
        # ========== 提示 ==========
        tip = QFrame()
        tip.setStyleSheet("""
            QFrame {
                background: #1A1A1A;
                border-radius: 10px;
            }
        """)
        tip_layout = QHBoxLayout(tip)
        tip_layout.setContentsMargins(18, 12, 18, 12)
        tip_layout.setSpacing(10)
        
        tip_icon = QLabel("i")
        tip_icon.setAlignment(Qt.AlignCenter)
        tip_icon.setFixedSize(24, 24)
        tip_icon.setStyleSheet("""
            background: white;
            color: #1A1A1A;
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
        """)
        tip_layout.addWidget(tip_icon)
        
        tip_text = QLabel("首次使用推荐选择「简单模式」")
        tip_text.setStyleSheet("color: white; font-size: 13px; background: transparent; border: none;")
        tip_layout.addWidget(tip_text)
        
        layout.addWidget(tip)
    
    def _select(self, mode):
        self.selected_mode = mode
        self.close()