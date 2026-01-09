# 粮食公告监控系统

## 功能介绍

该系统用于定期监控国家粮食交易中心的粮食相关公告，当发现包含指定关键词的新公告时，通过邮件发送通知。

## 项目结构

```
grain_announcement_monitor/
├── config/              # 配置模块
├── crawler/             # 爬虫模块
├── database/            # 数据库模块
├── notification/        # 通知模块
├── utils/               # 工具函数模块
├── .github/workflows/   # GitHub Actions工作流
├── main.py              # 主程序
├── requirements.txt     # 依赖文件
└── README.md            # 说明文档
```

## 安装和运行

### 本地运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置环境变量：
   ```bash
   # Linux/macOS
   export EMAIL_SMTP_SERVER="smtp.163.com"
   export EMAIL_SMTP_PORT="465"
   export EMAIL_USERNAME="your_email@example.com"
   export EMAIL_PASSWORD="your_email_password"
   export EMAIL_RECIPIENT="recipient_email@example.com"
   
   # Windows PowerShell
   $env:EMAIL_SMTP_SERVER="smtp.163.com"
   $env:EMAIL_SMTP_PORT="465"
   $env:EMAIL_USERNAME="your_email@example.com"
   $env:EMAIL_PASSWORD="your_email_password"
   $env:EMAIL_RECIPIENT="recipient_email@example.com"
   ```

3. 运行程序：
   ```bash
   python main.py
   ```

### GitHub Actions自动运行

1. 将项目上传到GitHub仓库

2. 在仓库的 `Settings > Secrets and variables > Actions` 中添加以下Secret：
   - `EMAIL_SMTP_SERVER`: 邮件服务器地址（如：smtp.163.com）
   - `EMAIL_SMTP_PORT`: 邮件服务器端口（如：465）
   - `EMAIL_USERNAME`: 发件人邮箱地址
   - `EMAIL_PASSWORD`: 发件人邮箱密码（注意：对于163等邮箱，需要使用授权码）
   - `EMAIL_RECIPIENT`: 收件人邮箱地址

3. GitHub Actions会按照 `.github/workflows/monitor.yml` 中定义的时间（每小时）自动运行程序

## 配置说明

配置文件位于 `config/__init__.py`，可以修改以下参数：

- `monitor_interval`: 监控间隔时间（秒），默认每小时运行一次
- `keywords`: 关键词列表，只有包含这些关键词的公告才会被监控
- `targets`: 监控目标配置，可以添加多个监控源

## 依赖说明

主要依赖包括：
- requests: 网络请求
- apscheduler: 定时任务
- beautifulsoup4: HTML解析（备用）

## 注意事项

1. 确保邮箱配置正确，特别是密码/授权码
2. 第一次运行时会自动创建数据库文件 `grain_announcements.db`
3. 日志会记录到 `monitor.log` 文件中
4. 可以通过修改 `.github/workflows/monitor.yml` 中的 `cron` 表达式来调整运行频率

## 安全建议

- 不要将敏感信息（如邮箱密码）硬编码到代码中
- 使用GitHub Secrets来存储敏感信息
- 定期更新邮箱密码和授权码
- 只授予程序必要的权限