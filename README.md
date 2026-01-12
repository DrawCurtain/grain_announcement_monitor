# 粮食公告监控系统

一个用于监控粮食交易公告的Python应用程序，可以定期抓取指定网站的粮食公告，并通过邮件通知符合条件的新公告。

## 功能特性

- ✅ 定期监控粮食交易公告
- ✅ 支持API和网页两种抓取方式
- ✅ 关键词过滤，只关注相关公告
- ✅ 数据持久化存储到SQLite数据库
- ✅ 新公告邮件通知
- ✅ 完善的错误处理和重试机制
- ✅ 详细的日志记录
- ✅ 模块化设计，易于扩展

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

1. 复制模板配置（如果需要）
2. 编辑`config/__init__.py`文件，根据需要修改配置
3. 设置环境变量用于敏感信息（邮件账号密码等）

### 环境变量配置

```bash
# 邮件配置
EMAIL_SMTP_SERVER=smtp.163.com
EMAIL_SMTP_PORT=465
EMAIL_USERNAME=your_email@163.com
EMAIL_PASSWORD=your_email_password
EMAIL_RECIPIENT=recipient@example.com
```

## 运行程序

### 执行一次监控任务

```bash
python main.py --no-scheduler
```

### 启动定时监控

```bash
python main.py
```

## 项目结构

```
grain_announcement_monitor/
├── config/              # 配置模块
├── crawler/             # 爬虫模块
├── database/            # 数据库模块
├── notification/        # 通知模块
├── utils/               # 工具模块
├── main.py              # 主程序
└── requirements.txt     # 依赖列表
```

## 技术栈

- Python 3.8+
- requests - HTTP请求
- BeautifulSoup4 - HTML解析
- apscheduler - 定时任务
- sqlite3 - 数据存储
- smtplib - 邮件发送

## 日志

日志文件默认生成在项目根目录下的`monitor.log`，采用滚动日志方式，每个日志文件最大10MB，保留最近5个日志文件。

## 扩展开发

### 添加新的监控目标

在`config/__init__.py`的`MONITOR_CONFIG['targets']`列表中添加新的监控目标配置。

### 添加新的爬虫类型

在`crawler`模块中实现新的爬虫类，并在`create_crawler`函数中注册。

## 注意事项

1. 请遵守网站的robots.txt规则
2. 合理设置监控间隔，避免对目标网站造成过大压力
3. 敏感信息（如邮箱密码）请通过环境变量配置，不要硬编码到代码中
4. 定期检查日志，确保程序正常运行

## 许可证

MIT License
