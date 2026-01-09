#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
粮食公告监控系统主程序
功能：定期监控指定网站的粮食相关公告，提取关键信息并存储到数据库
"""

import time
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

# 导入配置
from config import MONITOR_CONFIG

# 导入模块
from utils import setup_logger
from crawler import create_crawler
from database import DatabaseManager
from notification import NotificationManager

# 配置日志
logger = setup_logger()


# 监控任务
def monitor_task():
    """监控任务主函数"""
    logger.info("开始执行监控任务...")
    
    # 初始化组件
    db_manager = DatabaseManager()
    notifier = NotificationManager()
    
    all_new_announcements = []
    
    # 遍历所有监控目标
    for target in MONITOR_CONFIG['targets']:
        logger.info(f"监控目标: {target['name']}")
        
        try:
            # 创建爬虫实例
            crawler = create_crawler(target.get('type', 'api'))
            
            # 获取公告
            announcements = crawler.get_announcements(target)
            
            # 过滤包含关键词的公告
            keywords = MONITOR_CONFIG.get('keywords', [])
            target_keywords = target.get('keywords', [])
            all_keywords = list(set(keywords + target_keywords))  # 合并关键词，去重
            
            filtered_announcements = []
            for announcement in announcements:
                title = announcement.get('title', '')
                matched_keywords = [kw for kw in all_keywords if kw in title]
                if matched_keywords or not all_keywords:  # 如果没有关键词，不过滤
                    filtered_announcements.append(announcement)
            
            # 保存到数据库并收集新公告
            new_announcements = []
            for announcement in filtered_announcements:
                if db_manager.insert_announcement(announcement):
                    new_announcements.append(announcement)
            
            all_new_announcements.extend(new_announcements)
            
            if new_announcements:
                logger.info(f"监控目标 {target['name']} 发现 {len(new_announcements)} 条新公告")
            else:
                logger.info(f"监控目标 {target['name']} 没有发现新公告")
        except requests.RequestException as e:
            logger.error(f"监控目标 {target['name']} 网络连接失败: {str(e)}")
            logger.error(f"目标URL: {target.get('api_url', target.get('url', ''))}")
            logger.info("建议检查网络连接或目标网站是否可访问")
            continue
        except Exception as e:
            logger.error(f"处理监控目标 {target['name']} 时出错: {str(e)}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            continue
    
    # 发送邮件通知
    if all_new_announcements:
        notifier.notify_new_announcements(all_new_announcements, MONITOR_CONFIG.get('keywords', []))
    
    logger.info("监控任务执行完成")


# 主函数
def main():
    """主程序入口"""
    logger.info("粮食公告监控系统启动")
    
    # 初始化数据库
    try:
        db_manager = DatabaseManager()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败，程序退出: {str(e)}")
        return
    
    # 立即执行一次监控任务
    monitor_task()
    
    # 设置定时任务
    scheduler = BlockingScheduler()
    scheduler.add_job(
        monitor_task,
        'interval',
        seconds=MONITOR_CONFIG['monitor_interval'],
        id='grain_monitor_job',
        name='粮食公告监控任务'
    )
    
    logger.info(f"定时任务已设置，监控间隔: {MONITOR_CONFIG['monitor_interval']}秒")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("系统已停止")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}")
        scheduler.shutdown()


if __name__ == '__main__':
    main()
