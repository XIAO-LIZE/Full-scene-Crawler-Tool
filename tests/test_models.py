"""
数据模型测试

测试任务和结果模型的序列化、反序列化功能。
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.task import (
    SpiderTask, SpiderType, TaskStatus, StorageType,
    SpiderConfig, ParseRule, StorageConfig, ProxyConfig,
)
from src.models.result import TaskResult, ScrapedItem


class TestSpiderTask(unittest.TestCase):
    """爬虫任务模型测试"""

    def _make_sample_task(self) -> SpiderTask:
        """创建一个测试用的任务对象"""
        task = SpiderTask(
            task_id="test001",
            name="测试任务",
            description="用于单元测试",
            spider_type=SpiderType.STATIC,
        )
        task.spider_config.start_urls = ["https://example.com"]
        task.spider_config.timeout = 15
        task.parse_rules = [
            ParseRule(name="title", selector="h1", selector_type="css", attribute="text"),
            ParseRule(name="link", selector="a", selector_type="css", attribute="href"),
        ]
        task.storage_config.storage_type = StorageType.CSV
        task.storage_config.file_path = "data/output/test.csv"
        return task

    def test_to_dict(self):
        """测试序列化为字典"""
        task = self._make_sample_task()
        data = task.to_dict()

        self.assertEqual(data["task_id"], "test001")
        self.assertEqual(data["name"], "测试任务")
        self.assertEqual(data["spider_type"], "static")
        self.assertEqual(len(data["parse_rules"]), 2)

    def test_from_dict(self):
        """测试从字典反序列化"""
        task = self._make_sample_task()
        data = task.to_dict()

        # 从字典还原
        restored = SpiderTask.from_dict(data)

        self.assertEqual(restored.task_id, "test001")
        self.assertEqual(restored.name, "测试任务")
        self.assertEqual(restored.spider_type, SpiderType.STATIC)
        self.assertEqual(len(restored.parse_rules), 2)
        self.assertEqual(restored.parse_rules[0].name, "title")
        self.assertEqual(restored.spider_config.timeout, 15)

    def test_roundtrip(self):
        """测试序列化再反序列化后数据一致"""
        task = self._make_sample_task()
        data = task.to_dict()
        restored = SpiderTask.from_dict(data)

        # 再次序列化，应该和第一次一样
        self.assertEqual(task.to_dict(), restored.to_dict())


class TestTaskResult(unittest.TestCase):
    """任务结果模型测试"""

    def test_add_item(self):
        """测试添加数据项"""
        result = TaskResult(task_id="t1")
        item = ScrapedItem(
            item_id="item1",
            task_id="t1",
            url="https://example.com",
            data={"title": "测试"},
        )
        result.add_item(item)

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items_scraped, 1)

    def test_to_dict_and_back(self):
        """测试结果的序列化和反序列化"""
        result = TaskResult(task_id="t2")
        result.add_item(ScrapedItem(
            item_id="item1",
            task_id="t2",
            url="https://example.com",
            data={"title": "测试标题", "price": 9.9},
        ))
        result.complete()

        data = result.to_dict()
        restored = TaskResult.from_dict(data)

        self.assertEqual(restored.task_id, "t2")
        self.assertEqual(len(restored.items), 1)
        self.assertEqual(restored.items[0].data["title"], "测试标题")
        self.assertTrue(restored.success)
        self.assertIsNotNone(restored.completed_at)

    def test_error_result(self):
        """测试错误结果"""
        result = TaskResult(task_id="t3")
        result.set_error("连接超时", "Traceback...")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "连接超时")

    def test_to_dataframe_data(self):
        """测试转换为DataFrame格式"""
        result = TaskResult(task_id="t4")
        result.add_item(ScrapedItem(
            item_id="item1",
            task_id="t4",
            url="https://example.com/a",
            data={"name": "A"},
        ))
        result.add_item(ScrapedItem(
            item_id="item2",
            task_id="t4",
            url="https://example.com/b",
            data={"name": "B"},
        ))

        rows = result.to_dataframe_data()
        self.assertEqual(len(rows), 2)
        self.assertIn("_url", rows[0])
        self.assertEqual(rows[0]["name"], "A")


if __name__ == "__main__":
    unittest.main()
