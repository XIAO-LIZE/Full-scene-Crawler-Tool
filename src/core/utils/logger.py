"""
日志配置工具

统一管理爬虫工具的日志输出格式和级别。
"""
import os
import logging
import logging.handlers
from datetime import datetime


def setup_logger(
    name: str = "spider",
    level: int = logging.INFO,
    log_dir: str = "data/logs",
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    配置并返回一个Logger实例
    
    支持同时输出到控制台和文件，文件会自动轮转（防止日志文件过大）。
    
    Args:
        name: Logger名称
        level: 日志级别，默认INFO
        log_dir: 日志文件存放目录
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的旧日志文件数量
        
    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件输出（带轮转）
    if file_output:
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{name}.log")
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取已配置的Logger实例
    
    如果还没有配置过，会自动使用默认配置初始化。
    
    Args:
        name: Logger名称
        
    Returns:
        Logger实例
    """
    logger = logging.getLogger(name)

    # 如果没有handler，说明还没配置过
    if not logger.handlers:
        return setup_logger(name)

    return logger
