"""
SQLite存储
"""
import os
import json
import sqlite3
import logging
from typing import List, Dict, Any

from .base import BaseStorage
from ..models.result import TaskResult, ScrapedItem


logger = logging.getLogger(__name__)


class SqliteStorage(BaseStorage):
    """SQLite存储"""
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        db_path = self.config.db_connection_string
        if not db_path:
            db_path = "data/spider_data.db"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return sqlite3.connect(db_path)
    
    def _create_table(self, conn: sqlite3.Connection, fieldnames: List[str]):
        """创建表"""
        table_name = self.config.table_name
        
        # 构建列定义
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        columns.append("task_id TEXT NOT NULL")
        columns.append("_url TEXT")
        columns.append("_scraped_at TEXT")
        
        for field in fieldnames:
            if field not in ("task_id", "_url", "_scraped_at"):
                # 转义字段名
                safe_field = field.replace(" ", "_").replace("-", "_")
                columns.append(f'"{safe_field}" TEXT')
        
        # 创建表
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(columns)}
        )
        """
        
        conn.execute(create_sql)
        conn.commit()
    
    def save(self, result: TaskResult) -> bool:
        """保存结果到SQLite数据库"""
        try:
            if not result.items:
                logger.warning("No items to save")
                return False
            
            conn = self._get_connection()
            
            # 获取所有字段名
            fieldnames = set()
            for item in result.items:
                fieldnames.update(item.data.keys())
            fieldnames = sorted(fieldnames)
            
            # 创建表
            self._create_table(conn, fieldnames)
            
            # 准备插入数据
            table_name = self.config.table_name
            all_columns = ["task_id", "_url", "_scraped_at"] + [f.replace(" ", "_").replace("-", "_") for f in fieldnames]
            placeholders = ", ".join(["?"] * len(all_columns))
            columns_str = ", ".join([f'"{c}"' for c in all_columns])
            
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # 插入数据
            for item in result.items:
                values = [
                    item.task_id,
                    item.url,
                    item.scraped_at.isoformat(),
                ]
                
                for field in fieldnames:
                    value = item.data.get(field, "")
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    values.append(str(value) if value is not None else "")
                
                conn.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(result.items)} items to SQLite")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to SQLite: {e}")
            return False
    
    def load(self, task_id: str) -> TaskResult:
        """从SQLite数据库加载结果"""
        try:
            conn = self._get_connection()
            table_name = self.config.table_name
            
            # 检查表是否存在
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not cursor.fetchone():
                logger.warning(f"Table not found: {table_name}")
                conn.close()
                return TaskResult(task_id=task_id)
            
            # 查询数据
            cursor = conn.execute(f"SELECT * FROM {table_name} WHERE task_id = ?", (task_id,))
            rows = cursor.fetchall()
            
            # 获取列名
            column_names = [description[0] for description in cursor.description]
            
            result = TaskResult(task_id=task_id)
            
            for row in rows:
                row_dict = dict(zip(column_names, row))
                
                # 提取数据字段
                data = {}
                for key, value in row_dict.items():
                    if key not in ("id", "task_id", "_url", "_scraped_at"):
                        # 尝试解析JSON
                        try:
                            data[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            data[key] = value
                
                item = ScrapedItem(
                    item_id=str(row_dict.get("id", "")),
                    task_id=task_id,
                    url=row_dict.get("_url", ""),
                    data=data,
                )
                result.add_item(item)
            
            conn.close()
            
            logger.info(f"Loaded {len(result.items)} items from SQLite")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load from SQLite: {e}")
            return TaskResult(task_id=task_id)