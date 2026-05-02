"""
主窗口
"""
import sys
import logging
from typing import Optional, List
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QComboBox, QGroupBox, QFormLayout, QSpinBox,
    QCheckBox, QFileDialog, QMessageBox, QSplitter, QHeaderView,
    QStatusBar, QToolBar, QMenu, QMenuBar, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QAction, QIcon, QFont

from ..core.engine import get_engine
from ..models.task import SpiderTask, SpiderType, TaskStatus, StorageType
from ..models.result import TaskResult
from .dialogs.task_dialog import TaskDialog
from .widgets.log_widget import LogWidget
from .widgets.data_preview_widget import DataPreviewWidget


logger = logging.getLogger(__name__)


class SpiderThread(QThread):
    """爬虫线程"""
    task_started = Signal(str)
    task_finished = Signal(str, bool)
    task_error = Signal(str, str)
    
    def __init__(self, engine, task_id):
        super().__init__()
        self.engine = engine
        self.task_id = task_id
    
    def run(self):
        """运行爬虫任务"""
        self.task_started.emit(self.task_id)
        try:
            success = self.engine.run_task(self.task_id, async_run=False)
            self.task_finished.emit(self.task_id, success)
        except Exception as e:
            self.task_error.emit(self.task_id, str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.engine = get_engine()
        self.spider_threads: List[SpiderThread] = []
        
        self._init_ui()
        self._init_connections()
        self._init_engine_callbacks()
        self._load_tasks()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_task_table)
        self.refresh_timer.start(2000)  # 每2秒刷新一次
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("全场景爬虫工具 v1.0")
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_tool_bar()
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 任务管理选项卡
        self.task_tab = self._create_task_tab()
        self.tab_widget.addTab(self.task_tab, "任务管理")
        
        # 数据预览选项卡
        self.data_preview_widget = DataPreviewWidget()
        self.tab_widget.addTab(self.data_preview_widget, "数据预览")
        
        # 日志选项卡
        self.log_widget = LogWidget()
        self.tab_widget.addTab(self.log_widget, "运行日志")
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 添加状态信息标签
        self.status_label = QLabel("任务数: 0 | 运行中: 0")
        self.statusBar().addPermanentWidget(self.status_label)
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_task_action = QAction("新建任务", self)
        new_task_action.setShortcut("Ctrl+N")
        new_task_action.triggered.connect(self._create_task)
        file_menu.addAction(new_task_action)
        
        import_task_action = QAction("导入任务", self)
        import_task_action.triggered.connect(self._import_task)
        file_menu.addAction(import_task_action)
        
        export_task_action = QAction("导出任务", self)
        export_task_action.triggered.connect(self._export_task)
        file_menu.addAction(export_task_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 任务菜单
        task_menu = menubar.addMenu("任务")
        
        run_task_action = QAction("运行任务", self)
        run_task_action.setShortcut("F5")
        run_task_action.triggered.connect(self._run_selected_task)
        task_menu.addAction(run_task_action)
        
        stop_task_action = QAction("停止任务", self)
        stop_task_action.triggered.connect(self._stop_selected_task)
        task_menu.addAction(stop_task_action)
        
        delete_task_action = QAction("删除任务", self)
        delete_task_action.triggered.connect(self._delete_selected_task)
        task_menu.addAction(delete_task_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_task_table)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 新建任务按钮
        new_task_btn = QPushButton("新建任务")
        new_task_btn.clicked.connect(self._create_task)
        toolbar.addWidget(new_task_btn)
        
        toolbar.addSeparator()
        
        # 运行按钮
        run_btn = QPushButton("运行")
        run_btn.clicked.connect(self._run_selected_task)
        toolbar.addWidget(run_btn)
        
        # 停止按钮
        stop_btn = QPushButton("停止")
        stop_btn.clicked.connect(self._stop_selected_task)
        toolbar.addWidget(stop_btn)
        
        toolbar.addSeparator()
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_task_table)
        toolbar.addWidget(refresh_btn)
    
    def _create_task_tab(self) -> QWidget:
        """创建任务管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "任务ID", "任务名称", "类型", "状态", "已爬取", "创建时间", "操作"
        ])
        
        # 设置表格属性
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setSelectionMode(QTableWidget.SingleSelection)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.task_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("新建任务")
        create_btn.clicked.connect(self._create_task)
        button_layout.addWidget(create_btn)
        
        edit_btn = QPushButton("编辑任务")
        edit_btn.clicked.connect(self._edit_selected_task)
        button_layout.addWidget(edit_btn)
        
        run_btn = QPushButton("运行任务")
        run_btn.clicked.connect(self._run_selected_task)
        button_layout.addWidget(run_btn)
        
        stop_btn = QPushButton("停止任务")
        stop_btn.clicked.connect(self._stop_selected_task)
        button_layout.addWidget(stop_btn)
        
        delete_btn = QPushButton("删除任务")
        delete_btn.clicked.connect(self._delete_selected_task)
        button_layout.addWidget(delete_btn)
        
        view_result_btn = QPushButton("查看结果")
        view_result_btn.clicked.connect(self._view_selected_result)
        button_layout.addWidget(view_result_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _init_connections(self):
        """初始化信号连接"""
        self.task_table.doubleClicked.connect(self._edit_selected_task)
    
    def _init_engine_callbacks(self):
        """初始化引擎回调"""
        self.engine.register_callback("on_start", self._on_task_start)
        self.engine.register_callback("on_complete", self._on_task_complete)
        self.engine.register_callback("on_error", self._on_task_error)
        self.engine.register_callback("on_progress", self._on_task_progress)
    
    def _load_tasks(self):
        """加载任务"""
        self._refresh_task_table()
    
    def _refresh_task_table(self):
        """刷新任务表格"""
        tasks = self.engine.get_all_tasks()
        
        self.task_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # 任务ID
            self.task_table.setItem(row, 0, QTableWidgetItem(task.task_id))
            
            # 任务名称
            self.task_table.setItem(row, 1, QTableWidgetItem(task.name))
            
            # 类型
            type_item = QTableWidgetItem(task.spider_type.value)
            self.task_table.setItem(row, 2, type_item)
            
            # 状态
            status_item = QTableWidgetItem(task.status.value)
            if task.status == TaskStatus.RUNNING:
                status_item.setBackground(Qt.yellow)
            elif task.status == TaskStatus.COMPLETED:
                status_item.setBackground(Qt.green)
            elif task.status == TaskStatus.FAILED:
                status_item.setBackground(Qt.red)
            self.task_table.setItem(row, 3, status_item)
            
            # 已爬取数量
            self.task_table.setItem(row, 4, QTableWidgetItem(str(task.items_scraped)))
            
            # 创建时间
            created_at = task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else ""
            self.task_table.setItem(row, 5, QTableWidgetItem(created_at))
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            run_btn = QPushButton("运行")
            run_btn.clicked.connect(lambda checked, t=task: self._run_task(t.task_id))
            action_layout.addWidget(run_btn)
            
            stop_btn = QPushButton("停止")
            stop_btn.clicked.connect(lambda checked, t=task: self._stop_task(t.task_id))
            action_layout.addWidget(stop_btn)
            
            self.task_table.setCellWidget(row, 6, action_widget)
        
        # 更新状态栏
        running_count = len(self.engine.get_running_tasks())
        self.status_label.setText(f"任务数: {len(tasks)} | 运行中: {running_count}")
    
    def _create_task(self):
        """创建新任务"""
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            task = dialog.get_task()
            self.engine.update_task(task)
            self._refresh_task_table()
            self.log_widget.append_log(f"任务已创建: {task.name}")
    
    def _edit_selected_task(self):
        """编辑选中的任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        task = self.engine.get_task(task_id)
        
        if not task:
            QMessageBox.warning(self, "警告", "任务不存在")
            return
        
        dialog = TaskDialog(self, task)
        if dialog.exec() == QDialog.Accepted:
            updated_task = dialog.get_task()
            self.engine.update_task(updated_task)
            self._refresh_task_table()
            self.log_widget.append_log(f"任务已更新: {updated_task.name}")
    
    def _run_selected_task(self):
        """运行选中的任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        self._run_task(task_id)
    
    def _run_task(self, task_id: str):
        """运行任务"""
        task = self.engine.get_task(task_id)
        if not task:
            return
        
        if task.status == TaskStatus.RUNNING:
            QMessageBox.warning(self, "警告", "任务正在运行中")
            return
        
        # 在新线程中运行
        spider_thread = SpiderThread(self.engine, task_id)
        spider_thread.task_started.connect(self._on_task_started_ui)
        spider_thread.task_finished.connect(self._on_task_finished_ui)
        spider_thread.task_error.connect(self._on_task_error_ui)
        
        self.spider_threads.append(spider_thread)
        spider_thread.start()
        
        self.log_widget.append_log(f"开始运行任务: {task.name}")
    
    def _stop_selected_task(self):
        """停止选中的任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        self._stop_task(task_id)
    
    def _stop_task(self, task_id: str):
        """停止任务"""
        if self.engine.stop_task(task_id):
            self.log_widget.append_log(f"任务已停止: {task_id}")
            self._refresh_task_table()
        else:
            QMessageBox.warning(self, "警告", "无法停止任务")
    
    def _delete_selected_task(self):
        """删除选中的任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        task_name = self.task_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除任务 '{task_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.engine.delete_task(task_id)
            self._refresh_task_table()
            self.log_widget.append_log(f"任务已删除: {task_name}")
    
    def _view_selected_result(self):
        """查看选中任务的结果"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        
        result = self.engine.get_result(task_id)
        if result and result.items:
            self.data_preview_widget.set_result(result)
            self.tab_widget.setCurrentWidget(self.data_preview_widget)
        else:
            QMessageBox.information(self, "提示", "该任务暂无结果数据")
    
    def _import_task(self):
        """导入任务"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入任务", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                task = SpiderTask.from_dict(data)
                self.engine.update_task(task)
                self._refresh_task_table()
                self.log_widget.append_log(f"任务已导入: {task.name}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
    
    def _export_task(self):
        """导出任务"""
        selected_rows = self.task_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
            return
        
        row = selected_rows[0].row()
        task_id = self.task_table.item(row, 0).text()
        task = self.engine.get_task(task_id)
        
        if not task:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出任务", f"{task.name}.json", "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
                
                self.log_widget.append_log(f"任务已导出: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "全场景爬虫工具 v1.0\n\n"
            "功能强大的可视化爬虫工具\n"
            "支持静态页面、动态页面、API爬取\n"
            "支持CSV、JSON、SQLite、MySQL存储"
        )
    
    # 引擎回调函数
    def _on_task_start(self, task):
        """任务开始回调"""
        pass
    
    def _on_task_complete(self, task, result):
        """任务完成回调"""
        pass
    
    def _on_task_error(self, task, error):
        """任务错误回调"""
        pass
    
    def _on_task_progress(self, task, items_scraped):
        """任务进度回调"""
        pass
    
    # UI回调函数
    def _on_task_started_ui(self, task_id):
        """UI任务开始"""
        self.statusBar().showMessage(f"任务 {task_id} 正在运行...")
        self._refresh_task_table()
    
    def _on_task_finished_ui(self, task_id, success):
        """UI任务完成"""
        task = self.engine.get_task(task_id)
        if success:
            self.log_widget.append_log(f"任务完成: {task.name if task else task_id}")
            self.statusBar().showMessage("任务完成")
        else:
            self.log_widget.append_log(f"任务失败: {task.name if task else task_id}")
            self.statusBar().showMessage("任务失败")
        self._refresh_task_table()
    
    def _on_task_error_ui(self, task_id, error):
        """UI任务错误"""
        self.log_widget.append_log(f"任务错误 {task_id}: {error}")
        self.statusBar().showMessage("任务出错")
        self._refresh_task_table()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有运行中的任务
        for task in self.engine.get_running_tasks():
            self.engine.stop_task(task.task_id)
        
        # 关闭引擎
        self.engine.shutdown(wait=False)
        
        event.accept()