"""
爬取结果数据模型
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class ScrapedItem:
    """爬取的数据项"""
    item_id: str
    task_id: str
    url: str
    data: Dict[str, Any] = field(default_factory=dict)
    raw_html: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    depth: int = 0  # 爬取深度
    parent_url: str = ""  # 来源URL
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "item_id": self.item_id,
            "task_id": self.task_id,
            "url": self.url,
            "data": self.data,
            "raw_html": self.raw_html,
            "scraped_at": self.scraped_at.isoformat(),
            "depth": self.depth,
            "parent_url": self.parent_url,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScrapedItem":
        """从字典创建数据项"""
        item = cls(
            item_id=data["item_id"],
            task_id=data["task_id"],
            url=data["url"],
            data=data.get("data", {}),
            raw_html=data.get("raw_html", ""),
            depth=data.get("depth", 0),
            parent_url=data.get("parent_url", ""),
        )
        if "scraped_at" in data:
            item.scraped_at = datetime.fromisoformat(data["scraped_at"])
        return item


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    success: bool = True
    items: List[ScrapedItem] = field(default_factory=list)
    error_message: str = ""
    error_traceback: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    pages_crawled: int = 0
    items_scraped: int = 0
    items_failed: int = 0
    
    def add_item(self, item: ScrapedItem):
        """添加数据项"""
        self.items.append(item)
        self.items_scraped += 1
    
    def set_error(self, error_message: str, error_traceback: str = ""):
        """设置错误信息"""
        self.success = False
        self.error_message = error_message
        self.error_traceback = error_traceback
    
    def complete(self):
        """标记任务完成"""
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "items": [item.to_dict() for item in self.items],
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "pages_crawled": self.pages_crawled,
            "items_scraped": self.items_scraped,
            "items_failed": self.items_failed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """从字典创建结果"""
        result = cls(
            task_id=data["task_id"],
            success=data.get("success", True),
            error_message=data.get("error_message", ""),
            error_traceback=data.get("error_traceback", ""),
            pages_crawled=data.get("pages_crawled", 0),
            items_scraped=data.get("items_scraped", 0),
            items_failed=data.get("items_failed", 0),
        )
        
        if "items" in data:
            result.items = [ScrapedItem.from_dict(item) for item in data["items"]]
        
        if "started_at" in data:
            result.started_at = datetime.fromisoformat(data["started_at"])
        if "completed_at" in data and data["completed_at"]:
            result.completed_at = datetime.fromisoformat(data["completed_at"])
        
        return result
    
    def to_dataframe_data(self) -> List[Dict[str, Any]]:
        """转换为适合DataFrame的数据格式"""
        rows = []
        for item in self.items:
            row = {"_url": item.url, "_scraped_at": item.scraped_at.isoformat()}
            row.update(item.data)
            rows.append(row)
        return rows