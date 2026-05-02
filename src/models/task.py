"""
爬虫任务数据模型
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class SpiderType(Enum):
    """爬虫类型枚举"""
    STATIC = "static"  # 静态页面
    DYNAMIC = "dynamic"  # 动态页面（需要JS执行）
    API = "api"  # API接口


class StorageType(Enum):
    """存储类型枚举"""
    CSV = "csv"
    JSON = "json"
    SQLITE = "sqlite"
    MYSQL = "mysql"


class TaskStatus(Enum):
    """任务状态枚举"""
    CREATED = "created"  # 已创建
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    STOPPED = "stopped"  # 已停止


@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    http_proxy: str = ""
    https_proxy: str = ""
    proxy_list: List[str] = field(default_factory=list)  # 代理列表，用于轮换
    rotation: bool = False  # 是否轮换代理


@dataclass
class LoginConfig:
    """登录配置"""
    enabled: bool = False
    login_url: str = ""
    username: str = ""
    password: str = ""
    username_field: str = "username"
    password_field: str = "password"
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ScheduleConfig:
    """调度配置"""
    enabled: bool = False
    cron_expression: str = ""  # cron表达式
    interval_seconds: int = 0  # 间隔秒数
    run_once: bool = True  # 是否只运行一次


@dataclass
class SpiderConfig:
    """爬虫配置"""
    start_urls: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_times: int = 3
    retry_delay: int = 5
    delay_between_requests: float = 1.0  # 请求间隔（秒）
    follow_links: bool = False  # 是否跟踪链接
    max_depth: int = 1  # 最大爬取深度
    link_extractor_regex: str = ""  # 链接提取正则


@dataclass
class ParseRule:
    """解析规则"""
    name: str  # 字段名称
    selector: str  # 选择器（CSS或XPath）
    selector_type: str = "css"  # 选择器类型：css, xpath, regex
    attribute: str = "text"  # 提取属性：text, href, src等
    default_value: str = ""  # 默认值
    post_process: str = ""  # 后处理函数名


@dataclass
class StorageConfig:
    """存储配置"""
    storage_type: StorageType = StorageType.CSV
    file_path: str = ""  # 文件路径
    table_name: str = "spider_data"  # 数据库表名
    db_connection_string: str = ""  # 数据库连接字符串
    encoding: str = "utf-8"
    overwrite: bool = False  # 是否覆盖已有数据


@dataclass
class SpiderTask:
    """爬虫任务"""
    task_id: str
    name: str
    description: str = ""
    spider_type: SpiderType = SpiderType.STATIC
    status: TaskStatus = TaskStatus.CREATED
    
    # 配置
    spider_config: SpiderConfig = field(default_factory=SpiderConfig)
    parse_rules: List[ParseRule] = field(default_factory=list)
    storage_config: StorageConfig = field(default_factory=StorageConfig)
    proxy_config: ProxyConfig = field(default_factory=ProxyConfig)
    login_config: LoginConfig = field(default_factory=LoginConfig)
    schedule_config: ScheduleConfig = field(default_factory=ScheduleConfig)
    
    # 统计信息
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items_scraped: int = 0
    items_failed: int = 0
    pages_crawled: int = 0
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "spider_type": self.spider_type.value,
            "status": self.status.value,
            "spider_config": {
                "start_urls": self.spider_config.start_urls,
                "allowed_domains": self.spider_config.allowed_domains,
                "headers": self.spider_config.headers,
                "cookies": self.spider_config.cookies,
                "timeout": self.spider_config.timeout,
                "retry_times": self.spider_config.retry_times,
                "retry_delay": self.spider_config.retry_delay,
                "delay_between_requests": self.spider_config.delay_between_requests,
                "follow_links": self.spider_config.follow_links,
                "max_depth": self.spider_config.max_depth,
                "link_extractor_regex": self.spider_config.link_extractor_regex,
            },
            "parse_rules": [
                {
                    "name": rule.name,
                    "selector": rule.selector,
                    "selector_type": rule.selector_type,
                    "attribute": rule.attribute,
                    "default_value": rule.default_value,
                    "post_process": rule.post_process,
                }
                for rule in self.parse_rules
            ],
            "storage_config": {
                "storage_type": self.storage_config.storage_type.value,
                "file_path": self.storage_config.file_path,
                "table_name": self.storage_config.table_name,
                "db_connection_string": self.storage_config.db_connection_string,
                "encoding": self.storage_config.encoding,
                "overwrite": self.storage_config.overwrite,
            },
            "proxy_config": {
                "enabled": self.proxy_config.enabled,
                "http_proxy": self.proxy_config.http_proxy,
                "https_proxy": self.proxy_config.https_proxy,
                "proxy_list": self.proxy_config.proxy_list,
                "rotation": self.proxy_config.rotation,
            },
            "login_config": {
                "enabled": self.login_config.enabled,
                "login_url": self.login_config.login_url,
                "username": self.login_config.username,
                "password": self.login_config.password,
                "username_field": self.login_config.username_field,
                "password_field": self.login_config.password_field,
                "cookies": self.login_config.cookies,
                "headers": self.login_config.headers,
            },
            "schedule_config": {
                "enabled": self.schedule_config.enabled,
                "cron_expression": self.schedule_config.cron_expression,
                "interval_seconds": self.schedule_config.interval_seconds,
                "run_once": self.schedule_config.run_once,
            },
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "items_scraped": self.items_scraped,
            "items_failed": self.items_failed,
            "pages_crawled": self.pages_crawled,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpiderTask":
        """从字典创建任务"""
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            description=data.get("description", ""),
            spider_type=SpiderType(data.get("spider_type", "static")),
            status=TaskStatus(data.get("status", "created")),
        )
        
        # 解析spider_config
        if "spider_config" in data:
            sc = data["spider_config"]
            task.spider_config = SpiderConfig(
                start_urls=sc.get("start_urls", []),
                allowed_domains=sc.get("allowed_domains", []),
                headers=sc.get("headers", {}),
                cookies=sc.get("cookies", {}),
                timeout=sc.get("timeout", 30),
                retry_times=sc.get("retry_times", 3),
                retry_delay=sc.get("retry_delay", 5),
                delay_between_requests=sc.get("delay_between_requests", 1.0),
                follow_links=sc.get("follow_links", False),
                max_depth=sc.get("max_depth", 1),
                link_extractor_regex=sc.get("link_extractor_regex", ""),
            )
        
        # 解析parse_rules
        if "parse_rules" in data:
            task.parse_rules = [
                ParseRule(
                    name=rule["name"],
                    selector=rule["selector"],
                    selector_type=rule.get("selector_type", "css"),
                    attribute=rule.get("attribute", "text"),
                    default_value=rule.get("default_value", ""),
                    post_process=rule.get("post_process", ""),
                )
                for rule in data["parse_rules"]
            ]
        
        # 解析storage_config
        if "storage_config" in data:
            sc = data["storage_config"]
            task.storage_config = StorageConfig(
                storage_type=StorageType(sc.get("storage_type", "csv")),
                file_path=sc.get("file_path", ""),
                table_name=sc.get("table_name", "spider_data"),
                db_connection_string=sc.get("db_connection_string", ""),
                encoding=sc.get("encoding", "utf-8"),
                overwrite=sc.get("overwrite", False),
            )
        
        # 解析proxy_config
        if "proxy_config" in data:
            pc = data["proxy_config"]
            task.proxy_config = ProxyConfig(
                enabled=pc.get("enabled", False),
                http_proxy=pc.get("http_proxy", ""),
                https_proxy=pc.get("https_proxy", ""),
                proxy_list=pc.get("proxy_list", []),
                rotation=pc.get("rotation", False),
            )
        
        # 解析login_config
        if "login_config" in data:
            lc = data["login_config"]
            task.login_config = LoginConfig(
                enabled=lc.get("enabled", False),
                login_url=lc.get("login_url", ""),
                username=lc.get("username", ""),
                password=lc.get("password", ""),
                username_field=lc.get("username_field", "username"),
                password_field=lc.get("password_field", "password"),
                cookies=lc.get("cookies", {}),
                headers=lc.get("headers", {}),
            )
        
        # 解析schedule_config
        if "schedule_config" in data:
            sc = data["schedule_config"]
            task.schedule_config = ScheduleConfig(
                enabled=sc.get("enabled", False),
                cron_expression=sc.get("cron_expression", ""),
                interval_seconds=sc.get("interval_seconds", 0),
                run_once=sc.get("run_once", True),
            )
        
        # 解析时间字段
        if "created_at" in data:
            task.created_at = datetime.fromisoformat(data["created_at"])
        if "started_at" in data and data["started_at"]:
            task.started_at = datetime.fromisoformat(data["started_at"])
        if "completed_at" in data and data["completed_at"]:
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        task.items_scraped = data.get("items_scraped", 0)
        task.items_failed = data.get("items_failed", 0)
        task.pages_crawled = data.get("pages_crawled", 0)
        task.metadata = data.get("metadata", {})
        
        return task