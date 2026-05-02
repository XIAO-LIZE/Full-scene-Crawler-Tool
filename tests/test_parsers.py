"""
解析器模块测试

测试CSS、XPath、正则、JSON四种解析器的功能。
"""
import unittest
import json
import sys
import os

# 把项目根目录加入路径，方便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 直接导入解析器模块，避免经过 src.core.__init__ 触发 selenium 导入
from src.core.parsers.css_parser import CssParser
from src.core.parsers.xpath_parser import XPathParser
from src.core.parsers.regex_parser import RegexParser
from src.core.parsers.json_parser import JsonParser
# 确保不经过 engine -> spiders -> dynamic_spider 的导入链


# 测试用的HTML片段
SAMPLE_HTML = """
<html>
<head><title>测试页面</title></head>
<body>
    <div class="container">
        <h1 id="main-title">欢迎来到测试页面</h1>
        <ul class="news-list">
            <li class="item">
                <a href="https://example.com/1">第一条新闻</a>
                <span class="date">2024-01-15</span>
            </li>
            <li class="item">
                <a href="https://example.com/2">第二条新闻</a>
                <span class="date">2024-01-16</span>
            </li>
            <li class="item">
                <a href="https://example.com/3">第三条新闻</a>
                <span class="date">2024-01-17</span>
            </li>
        </ul>
        <div class="footer">
            <p>页脚信息</p>
        </div>
    </div>
</body>
</html>
"""

# 测试用的JSON数据
SAMPLE_JSON = json.dumps({
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {"id": 1, "title": "苹果", "price": 6.5},
            {"id": 2, "title": "香蕉", "price": 3.8},
            {"id": 3, "title": "橙子", "price": 5.2},
        ],
        "total": 3,
        "page": 1,
    }
}, ensure_ascii=False)


class TestCssParser(unittest.TestCase):
    """CSS选择器解析器测试"""

    def test_parse_text(self):
        """测试提取文本"""
        parser = CssParser("h1#main-title", attribute="text")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "欢迎来到测试页面")

    def test_parse_attribute(self):
        """测试提取属性"""
        parser = CssParser("ul.news-list li:first-child a", attribute="href")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "https://example.com/1")

    def test_parse_not_found(self):
        """测试未匹配到的情况"""
        parser = CssParser("div.not-exist", default_value="默认值")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "默认值")

    def test_parse_all(self):
        """测试提取所有匹配项"""
        parser = CssParser("ul.news-list li a", attribute="text")
        results = parser.parse_all(SAMPLE_HTML)
        self.assertEqual(len(results), 3)
        self.assertIn("第一条新闻", results)

    def test_parse_all_dates(self):
        """测试提取所有日期"""
        parser = CssParser("span.date", attribute="text")
        results = parser.parse_all(SAMPLE_HTML)
        self.assertEqual(results, ["2024-01-15", "2024-01-16", "2024-01-17"])


class TestXPathParser(unittest.TestCase):
    """XPath选择器解析器测试"""

    def test_parse_text(self):
        """测试提取文本"""
        parser = XPathParser("//h1[@id='main-title']/text()")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "欢迎来到测试页面")

    def test_parse_attribute(self):
        """测试提取属性"""
        parser = XPathParser("//ul[@class='news-list']//a/@href")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "https://example.com/1")

    def test_parse_not_found(self):
        """测试未匹配到的情况"""
        parser = XPathParser("//div[@class='不存在']", default_value="空")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "空")

    def test_parse_all(self):
        """测试提取所有匹配项"""
        parser = XPathParser("//ul[@class='news-list']//a/@href")
        results = parser.parse_all(SAMPLE_HTML)
        self.assertEqual(len(results), 3)
        self.assertIn("https://example.com/2", results)


class TestRegexParser(unittest.TestCase):
    """正则表达式解析器测试"""

    def test_parse_simple(self):
        """测试简单正则匹配"""
        parser = RegexParser(r"<title>(.*?)</title>")
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "测试页面")

    def test_parse_with_group(self):
        """测试带分组的正则"""
        parser = RegexParser(r'href="(https://example\.com/\d+)"')
        result = parser.parse(SAMPLE_HTML)
        self.assertEqual(result, "https://example.com/1")

    def test_parse_all(self):
        """测试提取所有匹配项"""
        parser = RegexParser(r'href="(https://example\.com/\d+)"')
        results = parser.parse_all(SAMPLE_HTML)
        self.assertEqual(len(results), 3)

    def test_parse_date(self):
        """测试匹配日期"""
        parser = RegexParser(r'(\d{4}-\d{2}-\d{2})')
        results = parser.parse_all(SAMPLE_HTML)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], "2024-01-15")


class TestJsonParser(unittest.TestCase):
    """JSON路径解析器测试"""

    def test_parse_simple_path(self):
        """测试简单路径"""
        parser = JsonParser("code")
        result = parser.parse(SAMPLE_JSON)
        self.assertEqual(result, 200)

    def test_parse_nested_path(self):
        """测试嵌套路径"""
        parser = JsonParser("data.total")
        result = parser.parse(SAMPLE_JSON)
        self.assertEqual(result, 3)

    def test_parse_array_index(self):
        """测试数组索引"""
        parser = JsonParser("data.items[0].title")
        result = parser.parse(SAMPLE_JSON)
        self.assertEqual(result, "苹果")

    def test_parse_not_found(self):
        """测试路径不存在"""
        parser = JsonParser("data.not_exist", default_value="无")
        result = parser.parse(SAMPLE_JSON)
        self.assertEqual(result, "无")

    def test_parse_all(self):
        """测试通配路径"""
        parser = JsonParser("data.items[].title")
        results = parser.parse_all(SAMPLE_JSON)
        self.assertEqual(results, ["苹果", "香蕉", "橙子"])

    def test_parse_all_prices(self):
        """测试提取所有价格"""
        parser = JsonParser("data.items[].price")
        results = parser.parse_all(SAMPLE_JSON)
        self.assertEqual(results, [6.5, 3.8, 5.2])

    def test_parse_invalid_json(self):
        """测试无效JSON"""
        parser = JsonParser("code", default_value=-1)
        result = parser.parse("这不是JSON")
        self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main()
