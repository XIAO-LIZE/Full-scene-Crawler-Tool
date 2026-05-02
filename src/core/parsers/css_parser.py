"""
CSS选择器解析器

使用 BeautifulSoup 的 CSS 选择器从 HTML 中提取数据。
"""
import logging
from typing import Any, Optional, List

from bs4 import BeautifulSoup, Tag

from .base import BaseParser


logger = logging.getLogger(__name__)


class CssParser(BaseParser):
    """
    CSS选择器解析器
    
    支持标准CSS选择器语法，如：
      - div.classname
      - #element-id
      - ul li a[href]
      - table tr td:nth-child(2)
    """

    def __init__(self, selector: str, attribute: str = "text", default_value: str = ""):
        super().__init__(selector, attribute, default_value)
        self._cached_content = None
        self._soup = None

    def _get_soup(self, content: str) -> BeautifulSoup:
        """解析HTML并缓存BeautifulSoup对象，内容不变时直接复用"""
        if self._cached_content != content:
            self._soup = BeautifulSoup(content, "lxml")
            self._cached_content = content
        return self._soup

    def parse(self, content: str) -> Optional[Any]:
        """使用CSS选择器提取第一个匹配元素"""
        try:
            soup = self._get_soup(content)
            elements = soup.select(self.selector)

            if not elements:
                return self.default_value

            value = self._extract_attribute(elements[0], self.attribute)
            return value if value else self.default_value

        except Exception as e:
            logger.error(f"CSS解析失败 [{self.selector}]: {e}")
            return self.default_value

    def parse_all(self, content: str) -> List[Any]:
        """使用CSS选择器提取所有匹配元素"""
        try:
            soup = self._get_soup(content)
            elements = soup.select(self.selector)

            results = []
            for elem in elements:
                value = self._extract_attribute(elem, self.attribute)
                if value:
                    results.append(value)

            return results

        except Exception as e:
            logger.error(f"CSS批量解析失败 [{self.selector}]: {e}")
            return []
