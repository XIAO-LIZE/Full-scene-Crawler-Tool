"""
存储模块测试

测试各存储类型的保存和加载功能。
"""
import unittest
import os
import json
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.task import StorageConfig, StorageType
from src.models.result import TaskResult, ScrapedItem
from src.storage.csv_storage import CsvStorage
from src.storage.json_storage import JsonStorage


def _make_sample_result() -> TaskResult:
    """生成测试用的爬取结果"""
    result = TaskResult(task_id="storage_test")
    result.add_item(ScrapedItem(
        item_id="item1",
        task_id="storage_test",
        url="https://example.com/1",
        data={"title": "标题一", "price": "9.9"},
    ))
    result.add_item(ScrapedItem(
        item_id="item2",
        task_id="storage_test",
        url="https://example.com/2",
        data={"title": "标题二", "price": "19.9"},
    ))
    result.complete()
    return result


class TestCsvStorage(unittest.TestCase):
    """CSV存储测试"""

    def test_save_and_load(self):
        """测试保存后再加载，数据一致"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.csv")
            config = StorageConfig(
                storage_type=StorageType.CSV,
                file_path=filepath,
            )

            # 保存
            storage = CsvStorage(config)
            result = _make_sample_result()
            ok = storage.save(result)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(filepath))

            # 加载
            loaded = storage.load("storage_test")
            self.assertEqual(len(loaded.items), 2)
            self.assertEqual(loaded.items[0].data["title"], "标题一")

    def test_save_empty_result(self):
        """测试保存空结果"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "empty.csv")
            config = StorageConfig(storage_type=StorageType.CSV, file_path=filepath)
            storage = CsvStorage(config)
            result = TaskResult(task_id="empty")
            ok = storage.save(result)
            self.assertFalse(ok)


class TestJsonStorage(unittest.TestCase):
    """JSON存储测试"""

    def test_save_and_load(self):
        """测试保存后再加载，数据一致"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            config = StorageConfig(
                storage_type=StorageType.JSON,
                file_path=filepath,
            )

            # 保存
            storage = JsonStorage(config)
            result = _make_sample_result()
            ok = storage.save(result)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(filepath))

            # 验证文件内容是合法JSON
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["task_id"], "storage_test")
            self.assertEqual(len(data["items"]), 2)

            # 加载
            loaded = storage.load("storage_test")
            self.assertEqual(len(loaded.items), 2)
            self.assertEqual(loaded.items[1].data["price"], "19.9")


if __name__ == "__main__":
    unittest.main()
