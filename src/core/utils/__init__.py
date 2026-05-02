"""
工具函数模块

提供URL处理、编码检测、日志配置等通用工具函数。
"""
from .url_utils import (
    normalize_url,
    is_valid_url,
    get_domain,
    is_same_domain,
    url_join,
    strip_fragment,
)
from .encoding import detect_encoding, safe_decode
from .logger import setup_logger, get_logger
from .retry import retry_request

__all__ = [
    # URL工具
    "normalize_url",
    "is_valid_url",
    "get_domain",
    "is_same_domain",
    "url_join",
    "strip_fragment",
    # 编码工具
    "detect_encoding",
    "safe_decode",
    # 日志工具
    "setup_logger",
    "get_logger",
    # 重试工具
    "retry_request",
]
