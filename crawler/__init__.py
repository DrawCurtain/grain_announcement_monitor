#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫模块
负责从目标网站获取公告数据
"""

from utils import retry, setup_logger
from config import MONITOR_CONFIG
import requests
import json
import os

logger = setup_logger()


class APICrawler:
    """
    API爬虫类
    用于从API获取公告数据
    """
    
    def __init__(self):
        self.request_config = MONITOR_CONFIG.get('request', {})
        self.timeout = self.request_config.get('timeout', 30)
        self.headers = self.request_config.get('headers', {})
        # 从环境变量获取代理配置
        self.proxies = {
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        }
        # 移除空值的代理配置
        self.proxies = {k: v for k, v in self.proxies.items() if v}
        
    @retry(max_retries=3, delay=2, backoff=2, exceptions=(requests.RequestException,))
    def fetch_announcements(self, api_url, tag_id, article_type):
        """
        从API获取公告列表
        
        :param api_url: API地址
        :param tag_id: 分类ID
        :param article_type: 文章类型
        :return: 公告列表
        """
        # 使用正确的API参数格式
        news_params = {
            "m": "tradeCenterOtherNewsList",
            "articleTypeID": article_type,
            "indexid": "1",
            "pagesize": "20"
        }
        
        payload = {"param": json.dumps(news_params)}
        
        logger.info(f"请求API: {api_url}, 参数: articleTypeID={article_type}")
        
        response = requests.post(
            api_url,
            data=payload,
            headers=self.headers,
            timeout=self.timeout,
            proxies=self.proxies
        )
        
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        
        if data.get('code') != '001':
            raise Exception(f"API返回错误: {data.get('msg', '未知错误')}")
        
        logger.info(f"成功获取 {len(data.get('data', []))} 条公告")
        return data.get('data', [])
    
    def parse_announcement(self, item):
        """
        解析公告数据
        
        :param item: 原始公告数据
        :return: 格式化后的公告数据
        """
        announcement = {
            'title': item.get('title', item.get('Title', '无标题')),
            'url': item.get('contentUrl', item.get('ContentUrl', '')),
            'pub_date': item.get('publishtime', item.get('PublishTime', '')),
            'source': item.get('source', ''),
            'tag_id': item.get('tag_id', ''),
            'article_type': item.get('article_type', '')
        }
        return announcement
    
    def get_announcements(self, target_config):
        """
        获取目标配置的公告列表
        
        :param target_config: 目标配置
        :return: 格式化后的公告列表
        """
        api_url = target_config.get('api_url')
        tag_id = target_config.get('tag_id')
        article_type = target_config.get('article_type')
        
        if not all([api_url, tag_id, article_type]):
            logger.error("目标配置不完整")
            return []
        
        raw_items = self.fetch_announcements(api_url, tag_id, article_type)
        
        announcements = []
        for item in raw_items:
            announcement = self.parse_announcement(item)
            if announcement:
                announcements.append(announcement)
        
        return announcements


class WebCrawler:
    """
    Web爬虫类
    用于从网页获取公告数据
    """
    
    def __init__(self):
        self.request_config = MONITOR_CONFIG.get('request', {})
        self.timeout = self.request_config.get('timeout', 30)
        self.headers = self.request_config.get('headers', {})
    
    @retry(max_retries=3, delay=2, backoff=2, exceptions=(requests.RequestException,))
    def fetch_page(self, url):
        """
        获取网页内容
        
        :param url: 网页地址
        :return: 网页内容
        """
        logger.info(f"请求网页: {url}")
        
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        return response.text
    
    def parse_page(self, html):
        """
        解析网页内容，提取公告信息
        
        :param html: 网页HTML内容
        :return: 公告列表
        """
        # 这里可以根据实际网页结构实现解析逻辑
        # 暂时返回空列表
        return []
    
    def get_announcements(self, target_config):
        """
        获取目标配置的公告列表
        
        :param target_config: 目标配置
        :return: 格式化后的公告列表
        """
        url = target_config.get('url')
        
        if not url:
            logger.error("目标配置缺少URL")
            return []
        
        html = self.fetch_page(url)
        return self.parse_page(html)


def create_crawler(crawler_type):
    """
    创建爬虫实例
    
    :param crawler_type: 爬虫类型（api 或 web）
    :return: 爬虫实例
    """
    if crawler_type == 'api':
        return APICrawler()
    elif crawler_type == 'web':
        return WebCrawler()
    else:
        raise ValueError(f"不支持的爬虫类型: {crawler_type}")