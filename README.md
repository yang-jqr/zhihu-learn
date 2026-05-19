# 知乎 DeepSeek 搜索结果爬虫

使用 Python + requests + BeautifulSoup4 抓取知乎搜索「DeepSeek」相关内容的标题、链接与摘要，并保存为 Markdown 格式。

## 技术栈

- **Python 3.8+**
- **requests**：HTTP 请求与会话管理
- **BeautifulSoup4**：HTML 解析
- **re / urllib**：文本清洗与 URL 处理

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/<你的用户名>/zhihu-deepseek-scraper.git
cd zhihu-deepseek-scraper
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行爬虫

```bash
python scraper.py
```

运行后会在 `articles/` 目录下生成：
- `README.md`：搜索结果汇总索引
- `article_01.md` ~ `article_10.md`：每条结果的独立 Markdown 文件

## 项目结构

```
zhihu-deepseek-scraper/
├── scraper.py           # 主爬虫逻辑
├── requirements.txt     # Python 依赖
├── .gitignore           # Git 忽略规则
├── articles/            # 输出目录（运行后生成）
│   ├── README.md        # 汇总索引
│   ├── article_01.md
│   └── ...
└── README.md            # 本文件
```

## 核心逻辑

1. **构造请求**：使用 `requests.Session` 携带现代浏览器 UA 访问知乎搜索页
2. **HTML 解析**：通过 BeautifulSoup 多选择器策略匹配搜索结果卡片
3. **数据提取**：解析标题、链接、作者、摘要
4. **持久化**：以 Markdown 格式保存，便于阅读与后续处理

## 学习收获

通过本项目可以掌握：

- 使用 `requests` 发送带 Headers 的 HTTP 请求
- 使用 `BeautifulSoup` 解析 HTML 并提取结构化数据
- 使用 `urllib.parse` 处理 URL 编码与拼接
- 文件读写与目录管理
- Git 版本控制与 GitHub 协作

## 注意事项

- 本项目仅用于学习 **网络请求与 HTML 解析**，爬取的是**公开搜索结果的标题与链接**
- 知乎存在反爬机制，若触发登录拦截，脚本会提示并保存 `debug_response.html` 供排查
- 请勿高频请求，运行间隔建议保持合理

## 后续可优化方向

- [ ] 增加 Cookie/登录态支持，获取更完整的结果
- [ ] 接入 Scrapy 框架，提升可扩展性
- [ ] 使用 Playwright/Selenium 处理动态渲染内容
- [ ] 将结果写入数据库（SQLite / PostgreSQL）
- [ ] 增加定时调度，实现每日自动抓取

## License

MIT
