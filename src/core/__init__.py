"""
核心模块

使用延迟导入，避免在只用到子模块（如parsers）时强制加载全部依赖（如selenium）。
需要SpiderEngine时请直接 from .engine import SpiderEngine。
"""

__all__ = ["SpiderEngine", "get_engine"]


def __getattr__(name):
    """延迟导入：只有真正访问 SpiderEngine / get_engine 时才触发 engine 模块加载"""
    if name in ("SpiderEngine", "get_engine"):
        from .engine import SpiderEngine, get_engine
        return get_engine if name == "get_engine" else SpiderEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
