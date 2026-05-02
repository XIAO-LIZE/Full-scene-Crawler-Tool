"""
正则表达式解析器

使用正则表达式从文本中提取数据。
"""
import re
import logging
from typing import Any, Optional, List

from .base import BaseParser


logger = logging.getLogger(__name__)


class RegexParser(BaseParser):
    """
    正则表达式解析器
    
    支持标准正则语法，如：
      - <title>(.*?)</title>
      - price["\\s:]+(\\d+\\.?\\d*)
      - (\\d{4}-\\d{2}-\\d{2})
    
    注意：selector 字段填正则表达式，attribute 字段不起作用。
    """

    def __init__(self, selector: str, attribute: str = "text", default_value: str = ""):
        super().__init__(selector, attribute, default_value)
        # 预编译正则表达式，提高多次匹配的效率
        try:
            self._pattern = re.compile(selector, re.DOTALL | re.IGNORECASE)
        except re.error as e:
            logger.warning(f"正则表达式编译失败，尝试不带标志编译: {e}")
            self._pattern = re.compile(selector)

    def parse(self, content: str) -> Optional[Any]:
        """使用正则表达式提取第一个匹配项"""
        try:
            match = self._pattern.search(content)

            if not match:
                return self.default_value

            # 如果有分组，返回第一个分组；否则返回整个匹配
            if match.lastindex and match.lastindex >= 1:
                return match.group(1).strip()
            return match.group(0).strip()

        except Exception as e:
            logger.error(f"正则解析失败 [{self.selector}]: {e}")
            return self.default_value

    def parse_all(self, content: str) -> List[Any]:
        """使用正则表达式提取所有匹配项"""
        try:
            matches = self._pattern.findall(content)

            if not matches:
                return []

            results = []
            for match in matches:
                # findall 返回分组元组时，取第一个分组
                if isinstance(match, tuple):
                    text = match[0].strip()
                else:
                    text = match.strip()

                if text:
                    results.append(text)

            return results

        except Exception as e:
            logger.error(f"正则批量解析失败 [{self.selector}]: {e}")
            return []
