"""
解析器基类
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List


class BaseParser(ABC):
    """
    数据解析器基类
    
    所有解析器都需要继承此类并实现 parse 方法。
    解析器负责从原始内容中提取结构化数据。
    """

    def __init__(self, selector: str, attribute: str = "text", default_value: str = ""):
        """
        初始化解析器
        
        Args:
            selector: 选择器表达式（CSS/XPath/正则/JSON路径）
            attribute: 要提取的属性名，如 text、href、src 等
            default_value: 未匹配到时返回的默认值
        """
        self.selector = selector
        self.attribute = attribute
        self.default_value = default_value

    @abstractmethod
    def parse(self, content: str) -> Optional[Any]:
        """
        解析内容并提取数据
        
        Args:
            content: 待解析的原始内容（HTML/JSON字符串等）
            
        Returns:
            提取到的值，未匹配则返回 default_value
        """
        pass

    @abstractmethod
    def parse_all(self, content: str) -> List[Any]:
        """
        解析内容并提取所有匹配的数据
        
        Args:
            content: 待解析的原始内容
            
        Returns:
            所有匹配结果的列表
        """
        pass

    def _extract_attribute(self, element, attribute: str) -> str:
        """
        从元素中提取指定属性的值
        
        Args:
            element: DOM元素
            attribute: 属性名
            
        Returns:
            属性值字符串
        """
        if attribute == "text":
            return element.get_text(strip=True) if hasattr(element, "get_text") else str(element)
        elif attribute == "html":
            return str(element)
        else:
            return element.get(attribute, self.default_value) if hasattr(element, "get") else self.default_value
