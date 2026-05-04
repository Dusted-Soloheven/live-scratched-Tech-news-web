# TechNewsAggregator

## 项目简介

`TechNewsAggregator` 是一个课程项目，用于从互联网上抓取科技新闻并生成网页展示结果。

本项目当前使用以下 3 个公开技术新闻源：

- TechCrunch
- The Verge
- Engadget

抓取结果会保存到 `scraped_news.json`，然后由本地 Flask 后端提供给网页动态展示。

## 当前已实现功能

- 从 3 个网站抓取公开的 RSS 或 Atom 新闻数据
- 动态网页展示新闻内容，而不是写死在 HTML 中
- 图片悬停缩放和点击放大
- 随机相关新闻评论展示
- 通过本地后端完成拼写检查
- 本地音频文件播放
- `robots.txt` 检查、限速和延迟控制

## 项目结构

- `app.py`: Flask 后端，提供网页和接口
- `Web.py`: 抓取工具类与合规请求逻辑
- `scraper.py`: 抓取脚本，生成 `scraped_news.json`
- `index.html`: 前端页面
- `scraped_news.json`: 最新抓取结果
- `assets/audio/`: 本地音频文件

## 运行环境

- Python 3
- `pip`

## 安装依赖

在项目目录中运行：

```bash
python -m pip install -r requirements.txt
```

## 运行步骤

### 1. 先抓取最新新闻

```bash
python scraper.py
```

运行后会生成或更新 `scraped_news.json`。

### 2. 启动本地后端

```bash
python app.py
```

默认访问地址：

- `http://127.0.0.1:5000/`

## 主要接口

- `GET /api/news`: 返回新闻数据
- `POST /api/spell-check`: 对输入单词执行拼写检查
- `GET /api/health`: 返回服务状态

## 与作业要求的对应关系

- 至少 3 个网站的 live information: 已实现，当前来源为 `TechCrunch`、`The Verge`、`Engadget`
- 图片、声音、随机评论: 已实现
- 图片放大功能: 已实现
- 拼写检查通过网站后端: 已实现
- 通过大语言模型生成并进行比较分析: 页面中保留了 LLM comparative analysis 区块
- 负责抓取要求: 已实现 `robots.txt` 检查、限速和延迟

## 文档位置

- 修复计划: `D:\我的文档\university\2026\CISC3016\proj\docs\repair-plan.md`
- 工单记录: `D:\我的文档\university\2026\CISC3016\proj\docs\work-orders.md`
- 合规说明: `D:\我的文档\university\2026\CISC3016\proj\docs\scraping-compliance.md`

## 注意事项

- 当前网页展示的数据来自最近一次运行 `scraper.py` 的结果。
- 如果想刷新网页内容，需要先重新运行抓取脚本，再刷新浏览器。
- 本项目为课程演示用途，不用于大规模抓取。
