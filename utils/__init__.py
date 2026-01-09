#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数模块
包含日志配置、重试装饰器和其他通用工具函数
"""

import logging
import time
import functools
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG


def setup_logger():
    """
    配置日志系统
    :return: 配置好的logger对象
    """
    logger = logging.getLogger('GrainMonitor')
    logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 文件日志
    file_handler = RotatingFileHandler(
        LOG_CONFIG['file_path'],
        maxBytes=LOG_CONFIG['max_bytes'],
        backupCount=LOG_CONFIG['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    重试装饰器
    
    :param max_retries: 最大重试次数
    :param delay: 初始延迟（秒）
    :param backoff: 延迟增长倍数
    :param exceptions: 捕获的异常类型
    :return: 装饰后的函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logger()
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"尝试 {max_retries} 次后失败: {str(e)}")
                        raise
                    
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}, 等待 {current_delay} 秒后重试")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def validate_url(url):
    """
    验证URL是否有效
    
    :param url: URL字符串
    :return: 验证结果（布尔值）
    """
    import re
    pattern = re.compile(r'^https?://[^\s]+$')
    return bool(pattern.match(url))


def format_datetime(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期时间
    
    :param dt_str: 日期时间字符串
    :param format_str: 目标格式
    :return: 格式化后的日期时间字符串
    """
    try:
        dt = time.strptime(dt_str, '%Y-%m-%d')
        return time.strftime(format_str, dt)
    except ValueError:
        return dt_str


def extract_domain(url):
    """
    从URL中提取域名
    
    :param url: URL字符串
    :return: 域名字符串
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc


def filter_keywords(text, keywords):
    """
    检查文本是否包含关键词列表中的任何一个关键词
    
    :param text: 待检查文本
    :param keywords: 关键词列表
    :return: 匹配的关键词列表
    """
    if not keywords:
        return []
    
    matched_keywords = [kw for kw in keywords if kw in text]
    return matched_keywords
