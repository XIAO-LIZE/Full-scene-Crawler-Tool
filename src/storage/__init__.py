"""
数据存储模块
"""
from ..models.task import StorageType
from .base import BaseStorage
from .csv_storage import CsvStorage
from .json_storage import JsonStorage
from .sqlite_storage import SqliteStorage
from .mysql_storage import MysqlStorage


# 存储类型映射
_STORAGE_MAP = {
    StorageType.CSV: CsvStorage,
    StorageType.JSON: JsonStorage,
    StorageType.SQLITE: SqliteStorage,
    StorageType.MYSQL: MysqlStorage,
}


def get_storage_class(storage_type: StorageType) -> type[BaseStorage]:
    """获取存储类"""
    storage_class = _STORAGE_MAP.get(storage_type)
    if not storage_class:
        raise ValueError(f"Unknown storage type: {storage_type}")
    return storage_class


__all__ = [
    "BaseStorage",
    "CsvStorage",
    "JsonStorage",
    "SqliteStorage",
    "MysqlStorage",
    "get_storage_class",
]