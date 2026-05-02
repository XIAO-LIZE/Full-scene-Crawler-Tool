"""
基础存储类
"""
from abc import ABC, abstractmethod
import logging

from ..models.task import StorageConfig
from ..models.result import TaskResult


logger = logging.getLogger(__name__)


class BaseStorage(ABC):
    """基础存储抽象类"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
    
    @abstractmethod
    def save(self, result: TaskResult) -> bool:
        """保存结果"""
        pass
    
    @abstractmethod
    def load(self, task_id: str) -> TaskResult:
        """加载结果"""
        pass