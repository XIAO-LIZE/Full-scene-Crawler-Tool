"""
JSON存储
"""
import os
import json
import logging
from typing import Dict, Any

from .base import BaseStorage
from ..models.result import TaskResult, ScrapedItem


logger = logging.getLogger(__name__)


class JsonStorage(BaseStorage):
    """JSON存储"""
    
    def save(self, result: TaskResult) -> bool:
        """保存结果到JSON文件"""
        try:
            file_path = self.config.file_path
            if not file_path:
                file_path = f"data/output/{result.task_id}.json"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 转换为字典
            data = result.to_dict()
            
            # 写入JSON文件
            with open(file_path, "w", encoding=self.config.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(result.items)} items to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
            return False
    
    def load(self, task_id: str) -> TaskResult:
        """从JSON文件加载结果"""
        try:
            file_path = self.config.file_path
            if not file_path:
                file_path = f"data/output/{task_id}.json"
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return TaskResult(task_id=task_id)
            
            with open(file_path, "r", encoding=self.config.encoding) as f:
                data = json.load(f)
            
            result = TaskResult.from_dict(data)
            logger.info(f"Loaded {len(result.items)} items from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            return TaskResult(task_id=task_id)