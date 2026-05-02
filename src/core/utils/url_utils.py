"""
URL处理工具函数

提供URL标准化、验证、域名提取等常用操作。
"""
from urllib.parse import urlparse, urljoin, urlunparse, quote, unquote
import re


def normalize_url(url: str) -> str:
    """
    标准化URL格式
    
    - 补全协议头（默认https）
    - 去掉末尾多余的斜杠
    - 统一为小写域名
    
    Args:
        url: 原始URL
        
    Returns:
        标准化后的URL
    """
    url = url.strip()

    # 补全协议头
    if not url.startswith(("http://", "https://", "//")):
        url = "https://" + url

    parsed = urlparse(url)

    # 域名转小写
    netloc = parsed.netloc.lower()

    # 去掉路径末尾的斜杠（但保留根路径 /）
    path = parsed.path.rstrip("/") or "/"

    return urlunparse((
        parsed.scheme,
        netloc,
        path,
        parsed.params,
        parsed.query,
        "",  # 去掉fragment
    ))


def is_valid_url(url: str) -> bool:
    """
    判断URL是否合法
    
    Args:
        url: 待检查的URL
        
    Returns:
        是否为合法的HTTP(S)链接
    """
    try:
        result = urlparse(url)
        return all([
            result.scheme in ("http", "https"),
            result.netloc,
        ])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """
    提取URL的域名部分
    
    Args:
        url: 完整URL
        
    Returns:
        域名字符串，如 "www.example.com"
    """
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_same_domain(url1: str, url2: str) -> bool:
    """
    判断两个URL是否属于同一域名
    
    Args:
        url1: 第一个URL
        url2: 第二个URL
        
    Returns:
        是否同域
    """
    return get_domain(url1) == get_domain(url2)


def url_join(base_url: str, relative_url: str) -> str:
    """
    拼接基础URL和相对路径
    
    Args:
        base_url: 基础URL，如 "https://example.com/page/"
        relative_url: 相对路径，如 "../other" 或 "/absolute"
        
    Returns:
        拼接后的完整URL
    """
    return urljoin(base_url, relative_url)


def strip_fragment(url: str) -> str:
    """
    去掉URL中的锚点部分（#后面的内容）
    
    Args:
        url: 原始URL
        
    Returns:
        去掉锚点后的URL
    """
    parsed = urlparse(url)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        "",
    ))


def encode_url(url: str) -> str:
    """
    对URL中的中文字符进行编码
    
    Args:
        url: 可能包含中文的URL
        
    Returns:
        编码后的URL
    """
    parsed = urlparse(url)
    # 只对path部分编码，保留协议和域名
    encoded_path = quote(parsed.path, safe="/:@!$&'()*+,;=-._~")
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        parsed.params,
        parsed.query,
        "",
    ))
