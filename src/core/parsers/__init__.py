"""
数据解析模块

提供多种解析器，支持CSS选择器、XPath、正则表达式和JSON路径提取。
"""
from .css_parser import CssParser
from .xpath_parser import XPathParser
from .regex_parser import RegexParser
from .json_parser import JsonParser
from .base import BaseParser

# 解析器类型映射
_PARSER_MAP = {
    "css": CssParser,
    "xpath": XPathParser,
    "regex": RegexParser,
    "json": JsonParser,
}


def get_parser_class(selector_type: str) -> type[BaseParser]:
    """根据选择器类型获取对应的解析器类"""
    parser_class = _PARSER_MAP.get(selector_type)
    if not parser_class:
        raise ValueError(f"不支持的选择器类型: {selector_type}")
    return parser_class


__all__ = [
    "BaseParser",
    "CssParser",
    "XPathParser",
    "RegexParser",
    "JsonParser",
    "get_parser_class",
]
