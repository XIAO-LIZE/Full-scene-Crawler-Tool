"""
爬虫引擎 - 核心爬虫调度器
"""
import uuid
import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

from ..models.task import SpiderTask, TaskStatus, SpiderType
from ..models.result import TaskResult, ScrapedItem
from .spiders import get_spider_class
from ..storage import get_storage_class


logger = logging.getLogger(__name__)


class SpiderEngine:
    """爬虫引擎"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, SpiderTask] = {}  # 任务字典
        self.results: Dict[str, TaskResult] = {}  # 结果字典
        self.futures: Dict[str, Future] = {}  # Future字典
        self._lock = threading.Lock()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_start": [],
            "on_progress": [],
            "on_item_scraped": [],
            "on_complete": [],
            "on_error": [],
        }
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调函数"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, **kwargs):
        """触发回调函数"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def create_task(self, name: str, spider_type: SpiderType = SpiderType.STATIC, **kwargs) -> SpiderTask:
        """创建新任务"""
        task_id = str(uuid.uuid4())[:8]
        task = SpiderTask(
            task_id=task_id,
            name=name,
            spider_type=spider_type,
            **kwargs
        )
        with self._lock:
            self.tasks[task_id] = task
        logger.info(f"Task created: {task_id} - {name}")
        return task
    
    def get_task(self, task_id: str) -> Optional[SpiderTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task: SpiderTask):
        """更新任务"""
        with self._lock:
            self.tasks[task.task_id] = task
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                if task_id in self.results:
                    del self.results[task_id]
                logger.info(f"Task deleted: {task_id}")
                return True
        return False
    
    def run_task(self, task_id: str, async_run: bool = True) -> bool:
        """运行任务"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False
        
        if task.status == TaskStatus.RUNNING:
            logger.warning(f"Task already running: {task_id}")
            return False
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.update_task(task)
        
        # 创建结果对象
        result = TaskResult(task_id=task_id)
        result.started_at = datetime.now()
        with self._lock:
            self.results[task_id] = result
        
        # 触发开始回调
        self._trigger_callbacks("on_start", task=task)
        
        if async_run:
            # 异步执行
            future = self.executor.submit(self._execute_task, task)
            with self._lock:
                self.futures[task_id] = future
            return True
        else:
            # 同步执行
            self._execute_task(task)
            return True
    
    def _execute_task(self, task: SpiderTask):
        """执行任务（内部方法）"""
        try:
            # 获取爬虫类
            spider_class = get_spider_class(task.spider_type)
            spider = spider_class(task, self)
            
            # 执行爬取
            result = spider.run()
            
            # 保存结果
            if result.success and result.items:
                self._save_results(task, result)
            
            # 更新任务状态
            if result.success:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
            
            task.completed_at = datetime.now()
            task.items_scraped = result.items_scraped
            task.items_failed = result.items_failed
            task.pages_crawled = result.pages_crawled
            self.update_task(task)
            
            # 触发完成回调
            self._trigger_callbacks("on_complete", task=task, result=result)
            
        except Exception as e:
            logger.exception(f"Task execution failed: {task.task_id}")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            self.update_task(task)
            
            # 更新结果
            with self._lock:
                if task.task_id in self.results:
                    self.results[task.task_id].set_error(str(e))
            
            # 触发错误回调
            self._trigger_callbacks("on_error", task=task, error=str(e))
    
    def _save_results(self, task: SpiderTask, result: TaskResult):
        """保存结果到存储"""
        try:
            storage_class = get_storage_class(task.storage_config.storage_type)
            storage = storage_class(task.storage_config)
            storage.save(result)
            logger.info(f"Results saved for task: {task.task_id}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status != TaskStatus.RUNNING:
            return False
        
        # 取消Future
        with self._lock:
            if task_id in self.futures:
                self.futures[task_id].cancel()
        
        # 更新任务状态
        task.status = TaskStatus.STOPPED
        task.completed_at = datetime.now()
        self.update_task(task)
        
        logger.info(f"Task stopped: {task_id}")
        return True
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.results.get(task_id)
    
    def get_all_tasks(self) -> List[SpiderTask]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_running_tasks(self) -> List[SpiderTask]:
        """获取正在运行的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.RUNNING]
    
    def on_item_scraped(self, task: SpiderTask, item: ScrapedItem):
        """数据项被爬取时的回调"""
        with self._lock:
            if task.task_id in self.results:
                self.results[task.task_id].add_item(item)
        
        task.items_scraped += 1
        self.update_task(task)
        
        # 触发进度回调
        self._trigger_callbacks("on_progress", task=task, items_scraped=task.items_scraped)
        self._trigger_callbacks("on_item_scraped", task=task, item=item)
    
    def on_page_crawled(self, task: SpiderTask, url: str):
        """页面被爬取时的回调"""
        task.pages_crawled += 1
        self.update_task(task)
    
    def shutdown(self, wait: bool = True):
        """关闭引擎"""
        # 停止所有运行中的任务
        for task in self.get_running_tasks():
            self.stop_task(task.task_id)
        
        # 关闭线程池
        self.executor.shutdown(wait=wait)
        logger.info("Spider engine shutdown")


# 全局引擎实例
_engine_instance: Optional[SpiderEngine] = None


def get_engine() -> SpiderEngine:
    """获取全局引擎实例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SpiderEngine()
    return _engine_instance