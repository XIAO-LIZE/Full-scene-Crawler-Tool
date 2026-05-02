"""
请求重试装饰器

提供可复用的重试逻辑，支持指数退避和自定义异常捕获。
"""
import time
import logging
from functools import wraps
from typing import Tuple, Type, Optional, Callable, Any

logger = logging.getLogger(__name__)


def retry_request(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    请求重试装饰器
    
    用法示例：
        @retry_request(max_retries=3, delay=1, backoff=2)
        def fetch(url):
            response = requests.get(url)
            response.raise_for_status()
            return response
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟秒数
        backoff: 退避倍数（每次重试延迟翻倍）
        exceptions: 需要捕获并重试的异常类型
        on_retry: 每次重试前的回调函数，签名为 on_retry(attempt, exception)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"请求失败 (第{attempt + 1}次)，{current_delay}秒后重试: {e}"
                        )

                        if on_retry:
                            try:
                                on_retry(attempt + 1, e)
                            except Exception:
                                pass

                        time.sleep(current_delay)
                        current_delay *= backoff  # 指数退避
                    else:
                        logger.error(f"请求失败，已重试{max_retries}次: {e}")

            raise last_exception

        return wrapper
    return decorator
