"""
编码检测与转换工具

处理网页内容的编码问题，避免乱码。
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 常见编码列表，按优先级排列
_COMMON_ENCODINGS = [
    "utf-8",
    "gbk",
    "gb2312",
    "gb18030",
    "big5",
    "euc-jp",
    "shift_jis",
    "euc-kr",
    "latin-1",
]


def detect_encoding(content: bytes, headers: Optional[dict] = None) -> str:
    """
    检测内容的编码方式
    
    优先从HTTP头部的Content-Type中提取，如果拿不到就逐个尝试解码。
    
    Args:
        content: 原始字节内容
        headers: HTTP响应头（可选）
        
    Returns:
        检测到的编码名称
    """
    # 1. 先从Content-Type头中提取
    if headers:
        content_type = headers.get("Content-Type", "")
        if "charset=" in content_type.lower():
            charset = content_type.lower().split("charset=")[-1].strip().rstrip(";")
            if charset:
                return charset

    # 2. 从HTML meta标签中提取
    head_bytes = content[:4096]
    try:
        head_str = head_bytes.decode("ascii", errors="ignore")
        # 匹配 <meta charset="xxx"> 或 <meta http-equiv="Content-Type" content="...charset=xxx">
        import re
        match = re.search(
            r'charset=["\']?([a-zA-Z0-9_-]+)',
            head_str,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)
    except Exception:
        pass

    # 3. 逐个尝试解码，选第一个能正常解码的
    for encoding in _COMMON_ENCODINGS:
        try:
            content.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue

    # 4. 兜底用utf-8
    return "utf-8"


def safe_decode(content: bytes, encoding: Optional[str] = None) -> str:
    """
    安全地将字节内容解码为字符串
    
    如果指定编码解码失败，会自动降级尝试其他编码。
    
    Args:
        content: 原始字节内容
        encoding: 指定的编码（可选）
        
    Returns:
        解码后的字符串
    """
    if not content:
        return ""

    # 如果指定了编码，先用它解码
    if encoding:
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            logger.warning(f"指定编码 {encoding} 解码失败，自动检测...")

    # 自动检测编码
    detected = detect_encoding(content)
    try:
        return content.decode(detected)
    except UnicodeDecodeError:
        # 最终兜底：忽略无法解码的字节
        logger.warning(f"编码 {detected} 解码仍有问题，使用errors='ignore'")
        return content.decode(detected, errors="ignore")
