"""
工具函数测试

测试URL处理、编码检测等工具函数。
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 直接导入工具模块，避免经过 src.core.__init__ 触发 selenium 导入
from src.core.utils.url_utils import (
    normalize_url, is_valid_url, get_domain, is_same_domain, url_join, strip_fragment,
)
from src.core.utils.encoding import detect_encoding, safe_decode


class TestUrlUtils(unittest.TestCase):
    """URL工具函数测试"""

    def test_normalize_url_adds_scheme(self):
        """测试自动补全协议头"""
        result = normalize_url("example.com/page")
        self.assertTrue(result.startswith("https://"))

    def test_normalize_url_removes_trailing_slash(self):
        """测试去掉末尾斜杠"""
        result = normalize_url("https://example.com/page/")
        self.assertEqual(result, "https://example.com/page")

    def test_normalize_url_keeps_root_slash(self):
        """测试保留根路径斜杠"""
        result = normalize_url("https://example.com/")
        self.assertEqual(result, "https://example.com/")

    def test_is_valid_url(self):
        """测试URL合法性判断"""
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://localhost:8080/path"))
        self.assertFalse(is_valid_url("not a url"))
        self.assertFalse(is_valid_url("ftp://example.com"))

    def test_get_domain(self):
        """测试域名提取"""
        self.assertEqual(get_domain("https://www.example.com/path"), "www.example.com")
        self.assertEqual(get_domain("http://localhost:3000"), "localhost:3000")

    def test_is_same_domain(self):
        """测试同域判断"""
        self.assertTrue(is_same_domain(
            "https://example.com/a",
            "https://example.com/b",
        ))
        self.assertFalse(is_same_domain(
            "https://example.com",
            "https://other.com",
        ))

    def test_url_join(self):
        """测试URL拼接"""
        result = url_join("https://example.com/page/", "../other")
        self.assertEqual(result, "https://example.com/other")

    def test_strip_fragment(self):
        """测试去掉锚点"""
        result = strip_fragment("https://example.com/page#section1")
        self.assertEqual(result, "https://example.com/page")


class TestEncoding(unittest.TestCase):
    """编码工具测试"""

    def test_detect_utf8(self):
        """测试检测UTF-8编码"""
        content = "你好世界".encode("utf-8")
        encoding = detect_encoding(content)
        self.assertEqual(encoding.lower().replace("-", ""), "utf8")

    def test_detect_gbk(self):
        """测试检测GBK编码"""
        content = "你好世界".encode("gbk")
        encoding = detect_encoding(content)
        # gbk 或 gb2312 都算对
        self.assertIn(encoding.lower().replace("-", ""), ["gbk", "gb2312", "gb18030"])

    def test_safe_decode(self):
        """测试安全解码"""
        content = "测试内容".encode("utf-8")
        result = safe_decode(content)
        self.assertEqual(result, "测试内容")

    def test_safe_decode_with_wrong_encoding(self):
        """测试指定错误编码时的降级处理"""
        content = "测试".encode("utf-8")
        # 指定错误的编码，应该自动降级
        result = safe_decode(content, encoding="ascii")
        # 虽然ascii解码会失败，但降级后应该能拿到内容
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
