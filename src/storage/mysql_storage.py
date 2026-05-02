"""
MySQL存储
"""
import json
import logging
from typing import List, Dict, Any

from .base import BaseStorage
from ..models.result import TaskResult, ScrapedItem


logger = logging.getLogger(__name__)


class MysqlStorage(BaseStorage):
    """MySQL存储"""
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            import pymysql
            
            # 解析连接字符串
            conn_string = self.config.db_connection_string
            if not conn_string:
                # 默认连接
                return pymysql.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="spider_data",
                    charset="utf8mb4"
                )
            
            # 解析mysql://user:password@host:port/database格式
            from urllib.parse import urlparse
            parsed = urlparse(conn_string)
            
            return pymysql.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 3306,
                user=parsed.username or "root",
                password=parsed.password or "",
                database=parsed.path.lstrip("/") if parsed.path else "spider_data",
                charset="utf8mb4"
            )
            
        except ImportError:
            logger.error("pymysql is not installed. Please install it with: pip install pymysql")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise
    
    def _create_table(self, conn, fieldnames: List[str]):
        """创建表"""
        table_name = self.config.table_name
        
        # 构建列定义
        columns = ["id INT AUTO_INCREMENT PRIMARY KEY"]
        columns.append("task_id VARCHAR(255) NOT NULL")
        columns.append("_url TEXT")
        columns.append("_scraped_at DATETIME")
        
        for field in fieldnames:
            if field not in ("task_id", "_url", "_scraped_at"):
                # 转义字段名
                safe_field = field.replace(" ", "_").replace("-", "_")
                columns.append(f'`{safe_field}` TEXT')
        
        # 创建表
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            {', '.join(columns)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        with conn.cursor() as cursor:
            cursor.execute(create_sql)
        conn.commit()
    
    def save(self, result: TaskResult) -> bool:
        """保存结果到MySQL数据库"""
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
            placeholders = ", ".join(["%s"] * len(all_columns))
            columns_str = ", ".join([f"`{c}`" for c in all_columns])
            
            insert_sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
            
            # 插入数据
            with conn.cursor() as cursor:
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
                    
                    cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(result.items)} items to MySQL")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to MySQL: {e}")
            return False
    
    def load(self, task_id: str) -> TaskResult:
        """从MySQL数据库加载结果"""
        try:
            conn = self._get_connection()
            table_name = self.config.table_name
            
            # 检查表是否存在
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s",
                    (table_name,)
                )
                if not cursor.fetchone():
                    logger.warning(f"Table not found: {table_name}")
                    conn.close()
                    return TaskResult(task_id=task_id)
            
            # 查询数据
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `{table_name}` WHERE task_id = %s", (task_id,))
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
            
            logger.info(f"Loaded {len(result.items)} items from MySQL")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load from MySQL: {e}")
            return TaskResult(task_id=task_id)