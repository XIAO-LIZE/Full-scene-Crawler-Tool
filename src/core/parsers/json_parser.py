"""
JSON路径解析器

支持点号分隔的路径从JSON数据中提取值，例如：
  - data.items[0].name
  - results[].title
  - response.code
"""
import json
import logging
from typing import Any, Optional, List

from .base import BaseParser


logger = logging.getLogger(__name__)


class JsonParser(BaseParser):
    """
    JSON路径解析器
    
    路径语法：
      - 点号分隔：data.items.name
      - 数组索引：data.items[0].title
      - 通配遍历：data.items[].name（返回列表）
    
    attribute 字段不起作用，selector 字段填JSON路径。
    """

    def __init__(self, selector: str, attribute: str = "text", default_value: str = ""):
        super().__init__(selector, attribute, default_value)
        self._cached_content = None  # 缓存的原始JSON字符串
        self._json_data = None       # 缓存的解析结果

    def _parse_json(self, content: str) -> Any:
        """解析JSON字符串并缓存结果，内容不变时直接复用"""
        if self._cached_content != content:
            self._json_data = json.loads(content)
            self._cached_content = content
        return self._json_data

    def _resolve_path(self, data: Any, path_parts: list) -> Any:
        """
        按路径逐级取值
        
        Args:
            data: 当前数据节点
            path_parts: 路径片段列表，如 ['data', 'items', '0', 'name']
            
        Returns:
            解析到的值
        """
        current = data

        for part in path_parts:
            if current is None:
                return self.default_value

            # 处理数组索引，如 items[0]
            if "[" in part and "]" in part:
                key = part.split("[")[0]
                index_str = part.split("[")[1].rstrip("]")

                # 先按key取值
                if key:
                    current = self._get_by_key(current, key)

                # 再按索引取值
                if current is not None and index_str:
                    try:
                        index = int(index_str)
                        current = current[index] if isinstance(current, list) else self.default_value
                    except (ValueError, IndexError):
                        return self.default_value
            else:
                current = self._get_by_key(current, part)

        return current if current is not None else self.default_value

    def _get_by_key(self, data: Any, key: str) -> Any:
        """按key从dict或list中取值"""
        if isinstance(data, dict):
            return data.get(key)
        elif isinstance(data, list):
            # 如果key是数字，当作索引
            try:
                return data[int(key)]
            except (ValueError, IndexError):
                return None
        return None

    def parse(self, content: str) -> Optional[Any]:
        """按JSON路径提取单个值"""
        try:
            data = self._parse_json(content)
            path_parts = self.selector.split(".")
            return self._resolve_path(data, path_parts)

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return self.default_value
        except Exception as e:
            logger.error(f"JSON路径解析失败 [{self.selector}]: {e}")
            return self.default_value

    def parse_all(self, content: str) -> List[Any]:
        """
        按JSON路径提取所有匹配值
        
        如果路径中包含通配索引 []，会遍历数组中所有元素。
        """
        try:
            data = self._parse_json(content)
            path_parts = self.selector.split(".")

            # 检查是否有通配符
            has_wildcard = any("[]" in part for part in path_parts)

            if not has_wildcard:
                # 没有通配符，直接取单个值
                result = self._resolve_path(data, path_parts)
                return [result] if result is not None else []

            # 有通配符，需要展开遍历
            return self._resolve_path_wildcard(data, path_parts)

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            logger.error(f"JSON批量解析失败 [{self.selector}]: {e}")
            return []

    def _resolve_path_wildcard(self, data: Any, path_parts: list) -> List[Any]:
        """处理带通配符的路径"""
        results = []
        self._collect_values(data, path_parts, 0, results)
        return results

    def _collect_values(self, current, parts: list, index: int, results: list):
        """递归收集通配路径下的所有值"""
        if index >= len(parts):
            if current is not None:
                results.append(current)
            return

        part = parts[index]

        if "[]" in part:
            # 通配符：遍历数组
            key = part.split("[")[0]
            if key:
                current = self._get_by_key(current, key)

            if isinstance(current, list):
                for item in current:
                    self._collect_values(item, parts, index + 1, results)
            return

        if "[" in part and "]" in part:
            # 普通数组索引
            key = part.split("[")[0]
            idx = int(part.split("[")[1].rstrip("]"))
            if key:
                current = self._get_by_key(current, key)
            if isinstance(current, list) and idx < len(current):
                self._collect_values(current[idx], parts, index + 1, results)
        else:
            # 普通key
            current = self._get_by_key(current, part)
            self._collect_values(current, parts, index + 1, results)
