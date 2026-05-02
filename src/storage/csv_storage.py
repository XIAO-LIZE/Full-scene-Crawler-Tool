"""
CSV存储
"""
import os
import csv
import logging
import json
from typing import List, Dict, Any

from .base import BaseStorage
from ..models.result import TaskResult, ScrapedItem


logger = logging.getLogger(__name__)


class CsvStorage(BaseStorage):
    """CSV存储"""
    
    def save(self, result: TaskResult) -> bool:
        """保存结果到CSV文件"""
        try:
            if not result.items:
                logger.warning("No items to save")
                return False
            
            # 确保目录存在
            file_path = self.config.file_path
            if not file_path:
                file_path = f"data/output/{result.task_id}.csv"
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 获取所有字段名
            fieldnames = set()
            for item in result.items:
                fieldnames.update(item.data.keys())
            
            # 添加元数据字段
            fieldnames = ["_url", "_scraped_at"] + sorted(fieldnames)
            
            # 写入CSV
            with open(file_path, "w", newline="", encoding=self.config.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in result.items:
                    row = {
                        "_url": item.url,
                        "_scraped_at": item.scraped_at.isoformat(),
                    }
                    # 处理复杂数据类型
                    for key, value in item.data.items():
                        if isinstance(value, (dict, list)):
                            row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            row[key] = value
                    writer.writerow(row)
            
            logger.info(f"Saved {len(result.items)} items to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
            return False
    
    def load(self, task_id: str) -> TaskResult:
        """从CSV文件加载结果"""
        try:
            file_path = self.config.file_path
            if not file_path:
                file_path = f"data/output/{task_id}.csv"
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return TaskResult(task_id=task_id)
            
            result = TaskResult(task_id=task_id)
            
            with open(file_path, "r", encoding=self.config.encoding) as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    item = ScrapedItem(
                        item_id=f"{task_id}_{len(result.items)}",
                        task_id=task_id,
                        url=row.get("_url", ""),
                        data={k: v for k, v in row.items() if not k.startswith("_")},
                    )
                    result.add_item(item)
            
            logger.info(f"Loaded {len(result.items)} items from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return TaskResult(task_id=task_id)