"""
任务配置对话框
"""
import uuid
from typing import Optional, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QGroupBox, QWidget, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog
)
from PySide6.QtCore import Qt

from ...models.task import (
    SpiderTask, SpiderType, TaskStatus, StorageType,
    SpiderConfig, ParseRule, StorageConfig, ProxyConfig,
    LoginConfig, ScheduleConfig
)


class TaskDialog(QDialog):
    """任务配置对话框"""
    
    def __init__(self, parent=None, task: Optional[SpiderTask] = None):
        super().__init__(parent)
        self.task = task
        self.is_edit_mode = task is not None
        
        if not self.task:
            self.task = SpiderTask(
                task_id=str(uuid.uuid4())[:8],
                name="新任务"
            )
        
        self._init_ui()
        self._load_task_data()
        
        if self.is_edit_mode:
            self.setWindowTitle("编辑任务")
        else:
            self.setWindowTitle("新建任务")
    
    def _init_ui(self):
        """初始化UI"""
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入任务名称")
        basic_layout.addRow("任务名称:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("请输入任务描述（可选）")
        basic_layout.addRow("任务描述:", self.description_edit)
        
        self.spider_type_combo = QComboBox()
        self.spider_type_combo.addItems(["静态页面", "动态页面", "API接口"])
        basic_layout.addRow("爬虫类型:", self.spider_type_combo)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 爬虫配置选项卡
        self.spider_config_tab = self._create_spider_config_tab()
        self.tab_widget.addTab(self.spider_config_tab, "爬虫配置")
        
        # 解析规则选项卡
        self.parse_rules_tab = self._create_parse_rules_tab()
        self.tab_widget.addTab(self.parse_rules_tab, "解析规则")
        
        # 存储配置选项卡
        self.storage_config_tab = self._create_storage_config_tab()
        self.tab_widget.addTab(self.storage_config_tab, "存储配置")
        
        # 代理配置选项卡
        self.proxy_config_tab = self._create_proxy_config_tab()
        self.tab_widget.addTab(self.proxy_config_tab, "代理配置")
        
        # 登录配置选项卡
        self.login_config_tab = self._create_login_config_tab()
        self.tab_widget.addTab(self.login_config_tab, "登录配置")
        
        # 调度配置选项卡
        self.schedule_config_tab = self._create_schedule_config_tab()
        self.tab_widget.addTab(self.schedule_config_tab, "调度配置")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._save_task)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_spider_config_tab(self) -> QWidget:
        """创建爬虫配置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 起始URL
        self.start_urls_edit = QTextEdit()
        self.start_urls_edit.setMaximumHeight(80)
        self.start_urls_edit.setPlaceholderText("每行一个URL")
        layout.addRow("起始URL:", self.start_urls_edit)
        
        # 允许的域名
        self.allowed_domains_edit = QLineEdit()
        self.allowed_domains_edit.setPlaceholderText("多个域名用逗号分隔")
        layout.addRow("允许的域名:", self.allowed_domains_edit)
        
        # 请求头
        self.headers_edit = QTextEdit()
        self.headers_edit.setMaximumHeight(80)
        self.headers_edit.setPlaceholderText("JSON格式，例如: {\"User-Agent\": \"Mozilla/5.0\"}")
        layout.addRow("请求头:", self.headers_edit)
        
        # 超时设置
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" 秒")
        layout.addRow("请求超时:", self.timeout_spin)
        
        # 重试次数
        self.retry_times_spin = QSpinBox()
        self.retry_times_spin.setRange(0, 10)
        self.retry_times_spin.setValue(3)
        layout.addRow("重试次数:", self.retry_times_spin)
        
        # 请求间隔
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(1.0)
        self.delay_spin.setSuffix(" 秒")
        layout.addRow("请求间隔:", self.delay_spin)
        
        # 跟踪链接
        self.follow_links_check = QCheckBox()
        layout.addRow("跟踪链接:", self.follow_links_check)
        
        # 最大深度
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 10)
        self.max_depth_spin.setValue(1)
        layout.addRow("最大深度:", self.max_depth_spin)
        
        return widget
    
    def _create_parse_rules_tab(self) -> QWidget:
        """创建解析规则选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 规则表格
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "字段名称", "选择器", "选择器类型", "属性", "默认值", "后处理"
        ])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.rules_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_rule_btn = QPushButton("添加规则")
        add_rule_btn.clicked.connect(self._add_parse_rule)
        button_layout.addWidget(add_rule_btn)
        
        remove_rule_btn = QPushButton("删除规则")
        remove_rule_btn.clicked.connect(self._remove_parse_rule)
        button_layout.addWidget(remove_rule_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_storage_config_tab(self) -> QWidget:
        """创建存储配置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 存储类型
        self.storage_type_combo = QComboBox()
        self.storage_type_combo.addItems(["CSV", "JSON", "SQLite", "MySQL"])
        self.storage_type_combo.currentIndexChanged.connect(self._on_storage_type_changed)
        layout.addRow("存储类型:", self.storage_type_combo)
        
        # 文件路径
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("输出文件路径")
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_file_path)
        file_path_layout.addWidget(browse_btn)
        layout.addRow("文件路径:", file_path_layout)
        
        # 表名（数据库）
        self.table_name_edit = QLineEdit()
        self.table_name_edit.setText("spider_data")
        self.table_name_edit.setPlaceholderText("数据库表名")
        layout.addRow("表名:", self.table_name_edit)
        
        # 数据库连接字符串
        self.db_connection_edit = QLineEdit()
        self.db_connection_edit.setPlaceholderText("数据库连接字符串")
        layout.addRow("连接字符串:", self.db_connection_edit)
        
        # 编码
        self.encoding_edit = QLineEdit()
        self.encoding_edit.setText("utf-8")
        layout.addRow("编码:", self.encoding_edit)
        
        # 覆盖已有数据
        self.overwrite_check = QCheckBox()
        layout.addRow("覆盖已有数据:", self.overwrite_check)
        
        return widget
    
    def _create_proxy_config_tab(self) -> QWidget:
        """创建代理配置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 启用代理
        self.proxy_enabled_check = QCheckBox()
        layout.addRow("启用代理:", self.proxy_enabled_check)
        
        # HTTP代理
        self.http_proxy_edit = QLineEdit()
        self.http_proxy_edit.setPlaceholderText("http://proxy:port")
        layout.addRow("HTTP代理:", self.http_proxy_edit)
        
        # HTTPS代理
        self.https_proxy_edit = QLineEdit()
        self.https_proxy_edit.setPlaceholderText("https://proxy:port")
        layout.addRow("HTTPS代理:", self.https_proxy_edit)
        
        # 代理列表
        self.proxy_list_edit = QTextEdit()
        self.proxy_list_edit.setMaximumHeight(100)
        self.proxy_list_edit.setPlaceholderText("每行一个代理地址")
        layout.addRow("代理列表:", self.proxy_list_edit)
        
        # 轮换代理
        self.proxy_rotation_check = QCheckBox()
        layout.addRow("轮换代理:", self.proxy_rotation_check)
        
        return widget
    
    def _create_login_config_tab(self) -> QWidget:
        """创建登录配置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 启用登录
        self.login_enabled_check = QCheckBox()
        layout.addRow("启用登录:", self.login_enabled_check)
        
        # 登录URL
        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText("登录页面URL")
        layout.addRow("登录URL:", self.login_url_edit)
        
        # 用户名
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("用户名")
        layout.addRow("用户名:", self.username_edit)
        
        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("密码")
        layout.addRow("密码:", self.password_edit)
        
        # 用户名字段名
        self.username_field_edit = QLineEdit()
        self.username_field_edit.setText("username")
        layout.addRow("用户名字段:", self.username_field_edit)
        
        # 密码字段名
        self.password_field_edit = QLineEdit()
        self.password_field_edit.setText("password")
        layout.addRow("密码字段:", self.password_field_edit)
        
        return widget
    
    def _create_schedule_config_tab(self) -> QWidget:
        """创建调度配置选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 启用调度
        self.schedule_enabled_check = QCheckBox()
        layout.addRow("启用调度:", self.schedule_enabled_check)
        
        # Cron表达式
        self.cron_edit = QLineEdit()
        self.cron_edit.setPlaceholderText("例如: 0 0 * * * (每天午夜)")
        layout.addRow("Cron表达式:", self.cron_edit)
        
        # 间隔秒数
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 86400)
        self.interval_spin.setSuffix(" 秒")
        layout.addRow("间隔秒数:", self.interval_spin)
        
        # 只运行一次
        self.run_once_check = QCheckBox()
        self.run_once_check.setChecked(True)
        layout.addRow("只运行一次:", self.run_once_check)
        
        return widget
    
    def _load_task_data(self):
        """加载任务数据"""
        task = self.task
        
        # 基本信息
        self.name_edit.setText(task.name)
        self.description_edit.setText(task.description)
        
        # 爬虫类型
        type_index = {
            SpiderType.STATIC: 0,
            SpiderType.DYNAMIC: 1,
            SpiderType.API: 2,
        }.get(task.spider_type, 0)
        self.spider_type_combo.setCurrentIndex(type_index)
        
        # 爬虫配置
        sc = task.spider_config
        self.start_urls_edit.setText("\n".join(sc.start_urls))
        self.allowed_domains_edit.setText(", ".join(sc.allowed_domains))
        
        import json
        if sc.headers:
            self.headers_edit.setText(json.dumps(sc.headers, ensure_ascii=False, indent=2))
        
        self.timeout_spin.setValue(sc.timeout)
        self.retry_times_spin.setValue(sc.retry_times)
        self.delay_spin.setValue(sc.delay_between_requests)
        self.follow_links_check.setChecked(sc.follow_links)
        self.max_depth_spin.setValue(sc.max_depth)
        
        # 解析规则
        self._load_parse_rules(task.parse_rules)
        
        # 存储配置
        stc = task.storage_config
        storage_index = {
            StorageType.CSV: 0,
            StorageType.JSON: 1,
            StorageType.SQLITE: 2,
            StorageType.MYSQL: 3,
        }.get(stc.storage_type, 0)
        self.storage_type_combo.setCurrentIndex(storage_index)
        self.file_path_edit.setText(stc.file_path)
        self.table_name_edit.setText(stc.table_name)
        self.db_connection_edit.setText(stc.db_connection_string)
        self.encoding_edit.setText(stc.encoding)
        self.overwrite_check.setChecked(stc.overwrite)
        
        # 代理配置
        pc = task.proxy_config
        self.proxy_enabled_check.setChecked(pc.enabled)
        self.http_proxy_edit.setText(pc.http_proxy)
        self.https_proxy_edit.setText(pc.https_proxy)
        self.proxy_list_edit.setText("\n".join(pc.proxy_list))
        self.proxy_rotation_check.setChecked(pc.rotation)
        
        # 登录配置
        lc = task.login_config
        self.login_enabled_check.setChecked(lc.enabled)
        self.login_url_edit.setText(lc.login_url)
        self.username_edit.setText(lc.username)
        self.password_edit.setText(lc.password)
        self.username_field_edit.setText(lc.username_field)
        self.password_field_edit.setText(lc.password_field)
        
        # 调度配置
        sc = task.schedule_config
        self.schedule_enabled_check.setChecked(sc.enabled)
        self.cron_edit.setText(sc.cron_expression)
        self.interval_spin.setValue(sc.interval_seconds)
        self.run_once_check.setChecked(sc.run_once)
    
    def _load_parse_rules(self, rules: List[ParseRule]):
        """加载解析规则"""
        self.rules_table.setRowCount(len(rules))
        
        for row, rule in enumerate(rules):
            self.rules_table.setItem(row, 0, QTableWidgetItem(rule.name))
            self.rules_table.setItem(row, 1, QTableWidgetItem(rule.selector))
            self.rules_table.setItem(row, 2, QTableWidgetItem(rule.selector_type))
            self.rules_table.setItem(row, 3, QTableWidgetItem(rule.attribute))
            self.rules_table.setItem(row, 4, QTableWidgetItem(rule.default_value))
            self.rules_table.setItem(row, 5, QTableWidgetItem(rule.post_process))
    
    def _add_parse_rule(self):
        """添加解析规则"""
        row = self.rules_table.rowCount()
        self.rules_table.setRowCount(row + 1)
        
        self.rules_table.setItem(row, 0, QTableWidgetItem(f"field_{row + 1}"))
        self.rules_table.setItem(row, 1, QTableWidgetItem(""))
        self.rules_table.setItem(row, 2, QTableWidgetItem("css"))
        self.rules_table.setItem(row, 3, QTableWidgetItem("text"))
        self.rules_table.setItem(row, 4, QTableWidgetItem(""))
        self.rules_table.setItem(row, 5, QTableWidgetItem(""))
    
    def _remove_parse_rule(self):
        """删除解析规则"""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)
    
    def _on_storage_type_changed(self, index: int):
        """存储类型改变"""
        # 根据存储类型显示/隐藏相关控件
        storage_type = StorageType(["csv", "json", "sqlite", "mysql"][index])
        
        if storage_type in (StorageType.CSV, StorageType.JSON):
            self.file_path_edit.setEnabled(True)
            self.table_name_edit.setEnabled(False)
            self.db_connection_edit.setEnabled(False)
        else:
            self.file_path_edit.setEnabled(False)
            self.table_name_edit.setEnabled(True)
            self.db_connection_edit.setEnabled(True)
    
    def _browse_file_path(self):
        """浏览文件路径"""
        storage_type = self.storage_type_combo.currentText()
        
        if storage_type == "CSV":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "选择CSV文件", "", "CSV文件 (*.csv)"
            )
        elif storage_type == "JSON":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "选择JSON文件", "", "JSON文件 (*.json)"
            )
        elif storage_type == "SQLite":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "选择SQLite数据库", "", "SQLite数据库 (*.db)"
            )
        else:
            return
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def _save_task(self):
        """保存任务"""
        # 验证输入
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入任务名称")
            return
        
        # 收集数据
        task = self.task
        task.name = self.name_edit.text().strip()
        task.description = self.description_edit.toPlainText().strip()
        
        # 爬虫类型
        type_map = {
            0: SpiderType.STATIC,
            1: SpiderType.DYNAMIC,
            2: SpiderType.API,
        }
        task.spider_type = type_map.get(self.spider_type_combo.currentIndex(), SpiderType.STATIC)
        
        # 爬虫配置
        import json
        
        task.spider_config.start_urls = [
            url.strip() for url in self.start_urls_edit.toPlainText().split("\n")
            if url.strip()
        ]
        
        domains_text = self.allowed_domains_edit.text().strip()
        if domains_text:
            task.spider_config.allowed_domains = [
                d.strip() for d in domains_text.split(",") if d.strip()
            ]
        
        headers_text = self.headers_edit.toPlainText().strip()
        if headers_text:
            try:
                task.spider_config.headers = json.loads(headers_text)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "警告", "请求头格式不正确")
                return
        
        task.spider_config.timeout = self.timeout_spin.value()
        task.spider_config.retry_times = self.retry_times_spin.value()
        task.spider_config.delay_between_requests = self.delay_spin.value()
        task.spider_config.follow_links = self.follow_links_check.isChecked()
        task.spider_config.max_depth = self.max_depth_spin.value()
        
        # 解析规则
        task.parse_rules = []
        for row in range(self.rules_table.rowCount()):
            name = self.rules_table.item(row, 0).text() if self.rules_table.item(row, 0) else ""
            selector = self.rules_table.item(row, 1).text() if self.rules_table.item(row, 1) else ""
            selector_type = self.rules_table.item(row, 2).text() if self.rules_table.item(row, 2) else "css"
            attribute = self.rules_table.item(row, 3).text() if self.rules_table.item(row, 3) else "text"
            default_value = self.rules_table.item(row, 4).text() if self.rules_table.item(row, 4) else ""
            post_process = self.rules_table.item(row, 5).text() if self.rules_table.item(row, 5) else ""
            
            if name and selector:
                task.parse_rules.append(ParseRule(
                    name=name,
                    selector=selector,
                    selector_type=selector_type,
                    attribute=attribute,
                    default_value=default_value,
                    post_process=post_process,
                ))
        
        # 存储配置
        storage_type_map = {
            0: StorageType.CSV,
            1: StorageType.JSON,
            2: StorageType.SQLITE,
            3: StorageType.MYSQL,
        }
        task.storage_config.storage_type = storage_type_map.get(
            self.storage_type_combo.currentIndex(), StorageType.CSV
        )
        task.storage_config.file_path = self.file_path_edit.text().strip()
        task.storage_config.table_name = self.table_name_edit.text().strip()
        task.storage_config.db_connection_string = self.db_connection_edit.text().strip()
        task.storage_config.encoding = self.encoding_edit.text().strip()
        task.storage_config.overwrite = self.overwrite_check.isChecked()
        
        # 代理配置
        task.proxy_config.enabled = self.proxy_enabled_check.isChecked()
        task.proxy_config.http_proxy = self.http_proxy_edit.text().strip()
        task.proxy_config.https_proxy = self.https_proxy_edit.text().strip()
        task.proxy_config.proxy_list = [
            p.strip() for p in self.proxy_list_edit.toPlainText().split("\n")
            if p.strip()
        ]
        task.proxy_config.rotation = self.proxy_rotation_check.isChecked()
        
        # 登录配置
        task.login_config.enabled = self.login_enabled_check.isChecked()
        task.login_config.login_url = self.login_url_edit.text().strip()
        task.login_config.username = self.username_edit.text().strip()
        task.login_config.password = self.password_edit.text()
        task.login_config.username_field = self.username_field_edit.text().strip()
        task.login_config.password_field = self.password_field_edit.text().strip()
        
        # 调度配置
        task.schedule_config.enabled = self.schedule_enabled_check.isChecked()
        task.schedule_config.cron_expression = self.cron_edit.text().strip()
        task.schedule_config.interval_seconds = self.interval_spin.value()
        task.schedule_config.run_once = self.run_once_check.isChecked()
        
        self.accept()
    
    def get_task(self) -> SpiderTask:
        """获取任务对象"""
        return self.task