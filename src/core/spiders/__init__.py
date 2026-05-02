"""
爬虫模块
"""
from ...models.task import SpiderType
from .base import BaseSpider
from .static_spider import StaticSpider
from .dynamic_spider import DynamicSpider
from .api_spider import ApiSpider


# 爬虫类型映射
_SPIDER_MAP = {
    SpiderType.STATIC: StaticSpider,
    SpiderType.DYNAMIC: DynamicSpider,
    SpiderType.API: ApiSpider,
}


def get_spider_class(spider_type: SpiderType) -> type[BaseSpider]:
    """获取爬虫类"""
    spider_class = _SPIDER_MAP.get(spider_type)
    if not spider_class:
        raise ValueError(f"Unknown spider type: {spider_type}")
    return spider_class


__all__ = [
    "BaseSpider",
    "StaticSpider", 
    "DynamicSpider",
    "ApiSpider",
    "get_spider_class",
]