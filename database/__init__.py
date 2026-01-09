#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库模块
负责公告数据的存储和查询
"""

import sqlite3
from utils import setup_logger
from config import MONITOR_CONFIG

logger = setup_logger()


class DatabaseManager:
    """
    数据库管理器类
    负责数据库的初始化、数据存储和查询
    """
    
    def __init__(self):
        self.db_path = MONITOR_CONFIG.get('storage', {}).get('file_path', 'grain_announcements.db')
        self.init_db()
    
    def init_db(self):
        """
        初始化数据库表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建公告表，兼容原有表结构
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS announcements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        content TEXT,
                        source TEXT,
                        publish_date TEXT NOT NULL,
                        crawl_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        keywords TEXT
                    )
                ''')
                
                conn.commit()
                logger.info(f"数据库初始化成功: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
    
    def insert_announcement(self, announcement):
        """
        插入公告数据
        
        :param announcement: 公告数据字典
        :return: 插入结果（True/False）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 兼容新旧表结构，使用publish_date字段名
                cursor.execute('''
                    INSERT OR IGNORE INTO announcements 
                    (title, url, publish_date, source) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    announcement.get('title'),
                    announcement.get('url'),
                    announcement.get('pub_date'),  # 从pub_date获取值，存入publish_date字段
                    announcement.get('source') or ''
                ))
                
                conn.commit()
                
                # 检查是否插入成功（未重复）
                if cursor.rowcount > 0:
                    logger.info(f"成功插入公告: {announcement.get('title')}")
                    return True
                else:
                    logger.debug(f"公告已存在，跳过插入: {announcement.get('title')}")
                    return False
        except Exception as e:
            logger.error(f"插入公告失败: {str(e)}")
            return False
    
    def batch_insert_announcements(self, announcements):
        """
        批量插入公告数据
        
        :param announcements: 公告数据列表
        :return: 成功插入的数量
        """
        if not announcements:
            return 0
        
        success_count = 0
        for announcement in announcements:
            if self.insert_announcement(announcement):
                success_count += 1
        
        return success_count
    
    def is_announcement_exists(self, url):
        """
        检查公告是否已存在
        
        :param url: 公告URL
        :return: 存在结果（True/False）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM announcements WHERE url = ?', (url,))
                result = cursor.fetchone()
                
                return result[0] > 0
        except Exception as e:
            logger.error(f"检查公告是否存在失败: {str(e)}")
            return False
    
    def get_latest_announcements(self, limit=10):
        """
        获取最新的公告
        
        :param limit: 获取数量限制
        :return: 公告列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM announcements 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取最新公告失败: {str(e)}")
            return []
    
    def get_all_announcements(self):
        """
        获取所有公告
        
        :return: 公告列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM announcements 
                    ORDER BY created_at DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取所有公告失败: {str(e)}")
            return []
    
    def delete_announcement(self, url):
        """
        删除指定URL的公告
        
        :param url: 公告URL
        :return: 删除结果（True/False）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM announcements WHERE url = ?', (url,))
                conn.commit()
                
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除公告失败: {str(e)}")
            return False
    
    def delete_latest_by_date(self, date_str):
        """
        删除指定日期的最新公告
        
        :param date_str: 日期字符串（格式：YYYY-MM-DD）
        :return: 删除结果（True/False）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 先获取指定日期的最新公告URL
                cursor.execute('''
                    SELECT url FROM announcements 
                    WHERE pub_date LIKE ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ''', (f'{date_str}%',))
                
                result = cursor.fetchone()
                if not result:
                    logger.info(f"未找到 {date_str} 日期的公告")
                    return False
                
                url = result[0]
                
                # 删除该公告
                cursor.execute('DELETE FROM announcements WHERE url = ?', (url,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"成功删除 {date_str} 日期的最新公告")
                    return True
                else:
                    return False
        except Exception as e:
            logger.error(f"删除最新公告失败: {str(e)}")
            return False
    
    def count_announcements(self):
        """
        获取公告总数
        
        :return: 公告总数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM announcements')
                result = cursor.fetchone()
                
                return result[0]
        except Exception as e:
            logger.error(f"获取公告总数失败: {str(e)}")
            return 0
    
    def get_announcements_by_keyword(self, keyword):
        """
        根据关键词查询公告
        
        :param keyword: 关键词
        :return: 匹配的公告列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM announcements 
                    WHERE title LIKE ? 
                    ORDER BY created_at DESC
                ''', (f'%{keyword}%',))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"根据关键词查询公告失败: {str(e)}")
            return []
    
    def clear_database(self):
        """
        清空数据库中的所有公告
        
        :return: 清空结果（True/False）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM announcements')
                conn.commit()
                
                logger.info("成功清空数据库")
                return True
        except Exception as e:
            logger.error(f"清空数据库失败: {str(e)}")
            return False