"""
XPath选择器解析器

使用 lxml 的 XPath 从 HTML 中提取数据。
"""
import logging
from typing import Any, Optional, List

from lxml import etree

from .base import BaseParser


logger = logging.getLogger(__name__)


class XPathParser(BaseParser):
    """
    XPath选择器解析器
    
    支持标准XPath语法，如：
      - //div[@class='title']
      - //a/@href
      - //text()
      - //table//tr[1]/td
    """

    def __init__(self, selector: str, attribute: str = "text", default_value: str = ""):
        super().__init__(selector, attribute, default_value)
        self._cached_content = None  # 缓存的原始内容
        self._tree = None            # 缓存的解析树

    def _get_tree(self, content: str) -> etree._Element:
        """解析HTML并缓存lxml树结构，内容不变时直接复用"""
        if self._cached_content != content:
            self._tree = etree.HTML(content)
            self._cached_content = content
        return self._tree

    def _extract_text(self, element) -> str:
        """从元素中提取文本内容"""
        if isinstance(element, etree._Element):
            return etree.tostring(element, method="text", encoding="unicode").strip()
        return str(element).strip()

    def parse(self, content: str) -> Optional[Any]:
        """使用XPath提取第一个匹配元素"""
        try:
            tree = self._get_tree(content)
            results = tree.xpath(self.selector)

            if not results:
                return self.default_value

            first = results[0]

            # xpath可能返回字符串（如 //text() 或 @attr）
            if isinstance(first, str):
                return first.strip() if first.strip() else self.default_value

            # 返回的是元素
            if self.attribute == "text":
                value = self._extract_text(first)
            else:
                value = first.get(self.attribute, self.default_value)

            return value if value else self.default_value

        except Exception as e:
            logger.error(f"XPath解析失败 [{self.selector}]: {e}")
            return self.default_value

    def parse_all(self, content: str) -> List[Any]:
        """使用XPath提取所有匹配元素"""
        try:
            tree = self._get_tree(content)
            results = tree.xpath(self.selector)

            values = []
            for item in results:
                if isinstance(item, str):
                    text = item.strip()
                    if text:
                        values.append(text)
                else:
                    if self.attribute == "text":
                        text = self._extract_text(item)
                    else:
                        text = item.get(self.attribute, "")
                    if text:
                        values.append(text)

            return values

        except Exception as e:
            logger.error(f"XPath批量解析失败 [{self.selector}]: {e}")
            return []
