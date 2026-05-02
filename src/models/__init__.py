"""
数据模型模块
"""
from .task import (
    SpiderTask, SpiderType, TaskStatus, StorageType,
    SpiderConfig, ParseRule, StorageConfig, ProxyConfig,
    LoginConfig, ScheduleConfig
)
from .result import TaskResult, ScrapedItem

__all__ = [
    "SpiderTask", "SpiderType", "TaskStatus", "StorageType",
    "SpiderConfig", "ParseRule", "StorageConfig", "ProxyConfig",
    "LoginConfig", "ScheduleConfig",
    "TaskResult", "ScrapedItem"
]