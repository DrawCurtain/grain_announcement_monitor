#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知模块
负责发送邮件通知
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import setup_logger
from config import MONITOR_CONFIG

logger = setup_logger()


class EmailNotification:
    """
    邮件通知类
    负责发送邮件通知
    """
    
    def __init__(self):
        self.email_config = MONITOR_CONFIG.get('notification', {}).get('email', {})
        self.enabled = MONITOR_CONFIG.get('notification', {}).get('enabled', False)
        
        if not self.enabled:
            logger.info("邮件通知已禁用")
        
        self.smtp_server = self.email_config.get('smtp_server')
        self.smtp_port = self.email_config.get('smtp_port', 465)
        self.username = self.email_config.get('username')
        self.password = self.email_config.get('password')
        self.recipient = self.email_config.get('recipient')
    
    def send_email(self, subject, content):
        """
        发送邮件
        
        :param subject: 邮件主题
        :param content: 邮件内容
        :return: 发送结果（True/False）
        """
        if not self.enabled:
            logger.info("邮件通知已禁用，跳过发送")
            return False
        
        if not all([self.smtp_server, self.username, self.password, self.recipient]):
            logger.error("邮件配置不完整，无法发送邮件")
            return False
        
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = self.recipient
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"成功发送邮件到 {self.recipient}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def send_announcement_notification(self, announcements, keywords=None):
        """
        发送公告通知邮件
        
        :param announcements: 公告列表
        :param keywords: 关键词列表（可选）
        :return: 发送结果（True/False）
        """
        if not announcements:
            logger.info("没有新公告需要通知")
            return False
        
        # 如果提供了关键词，过滤包含关键词的公告
        if keywords:
            filtered_announcements = []
            for announcement in announcements:
                title = announcement.get('title', '')
                matched_keywords = [kw for kw in keywords if kw in title]
                if matched_keywords:
                    announcement['matched_keywords'] = matched_keywords
                    filtered_announcements.append(announcement)
            
            if not filtered_announcements:
                logger.info("没有匹配关键词的新公告需要通知")
                return False
            
            announcements = filtered_announcements
        
        # 构建邮件内容
        subject = f"【粮食公告监控】发现 {len(announcements)} 条新公告"
        
        content = "\n" + "="*60 + "\n"
        content += f"新公告通知\n"
        content += "="*60 + "\n\n"
        
        for announcement in announcements:
            content += f"标题: {announcement.get('title')}\n"
            content += f"链接: {announcement.get('url')}\n"
            content += f"发布日期: {announcement.get('pub_date')}\n"
            if 'matched_keywords' in announcement:
                content += f"匹配关键词: {', '.join(announcement['matched_keywords'])}\n"
            content += "-"*60 + "\n"
        
        content += f"\n总计: {len(announcements)} 条新公告\n"
        content += f"监控时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return self.send_email(subject, content)


class NotificationManager:
    """
    通知管理器类
    负责管理多种通知方式
    """
    
    def __init__(self):
        self.email_notifier = EmailNotification()
    
    def notify_new_announcements(self, announcements, keywords=None):
        """
        通知新公告
        
        :param announcements: 公告列表
        :param keywords: 关键词列表（可选）
        :return: 通知结果（True/False）
        """
        # 目前只支持邮件通知
        return self.email_notifier.send_announcement_notification(announcements, keywords)


# 导入time模块，用于格式化时间
import time