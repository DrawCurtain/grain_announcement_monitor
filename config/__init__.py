import os

# 粮食公告监控系统配置模块

# 监控目标配置
MONITOR_CONFIG = {
    # 监控目标配置
    "targets": [
        {
            "name": "国家粮食交易中心-交易公告",
            "type": "api",
            "api_url": "https://www.grainmarket.com.cn/centerweb/getData",
            "tag_id": "3",  # 交易公告分类
            "article_type": "4",  # 国家政策粮食交易公告
            "keywords": ["进口大豆", "大豆", "竞价销售"]
        }
    ],
    
    # 监控间隔时间（秒）
    "monitor_interval": 3600,  # 默认每小时监控一次
    
    # 关键词过滤（可选，只监控包含这些关键词的公告）
    "keywords": [
        "进口大豆"
        # 可以添加更多关键词
    ],
    
    # 数据存储配置
    "storage": {
        "type": "sqlite",  # 支持 sqlite, mysql 等
        "file_path": "grain_announcements.db"  # SQLite数据库文件路径
    },
    
    # 通知配置
    "notification": {
        "enabled": True,
        "email": {
            "smtp_server": os.environ.get("EMAIL_SMTP_SERVER", "smtp.163.com"),
            "smtp_port": int(os.environ.get("EMAIL_SMTP_PORT", 465)),
            "username": os.environ.get("EMAIL_USERNAME", ""),
            "password": os.environ.get("EMAIL_PASSWORD", ""),
            "recipient": os.environ.get("EMAIL_RECIPIENT", "")
        }
    },
    
    # 网络请求配置
    "request": {
        "timeout": 30,  # 请求超时时间（秒）
        "retry_count": 3,  # 重试次数
        "retry_delay": 2,  # 重试间隔（秒）
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    }
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file_path": "monitor.log",  # 日志文件路径
    "max_bytes": 10 * 1024 * 1024,  # 日志文件最大大小（10MB）
    "backup_count": 5  # 保留的日志备份数量
}
