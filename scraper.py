"""
知乎 DeepSeek 搜索结果爬虫
目标：获取知乎搜索 "DeepSeek" 相关内容的标题、链接与摘要
技术栈：requests + BeautifulSoup4
"""

import os
import re
import time
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup


class ZhihuScraper:
    def __init__(self, keyword: str, limit: int = 10):
        self.keyword = keyword
        self.limit = limit
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.zhihu.com/",
        })
        self.results = []

    def fetch_search_page(self) -> str:
        """请求知乎搜索结果页"""
        encoded_keyword = quote(self.keyword)
        url = f"https://www.zhihu.com/search?type=content&q={encoded_keyword}"
        print(f"[请求] {url}")
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"[网络错误] 请求失败: {e}")
            return ""

    def _is_login_page(self, html: str) -> bool:
        """简单检测是否被重定向到登录页"""
        return (
            "登录" in html and "扫码登录" in html
        ) or "login" in html.lower()[:5000]

    def parse_results(self, html: str) -> list[dict]:
        """解析搜索结果卡片"""
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # 知乎搜索结果常见容器选择器（按优先级尝试）
        selectors = [
            'div[data-za-detail-view-path-module="SearchItem"]',
            'div.SearchResult-Card',
            'div.Search-container .Card',
            '.ContentItem',
        ]

        cards = []
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                print(f"[解析] 使用选择器: {sel}, 共 {len(cards)} 条")
                break

        if not cards:
            print("[警告] 未匹配到搜索结果卡片，可能页面结构已变更或触发反爬")
            return articles

        for card in cards[:self.limit]:
            # 提取标题与链接
            title_tag = (
                card.select_one('a[data-za-detail-view-id]')
                or card.select_one('.ContentItem-title a')
                or card.select_one('a[data-za-detail-view-path-module]')
            )
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            link = urljoin("https://www.zhihu.com", href) if href else ""

            # 提取摘要/正文片段
            excerpt_tag = (
                card.select_one('.RichContent-inner')
                or card.select_one('.SearchResult-abstract')
                or card.select_one('.ContentItem-meta + div')
            )
            excerpt = ""
            if excerpt_tag:
                excerpt = re.sub(r"\s+", " ", excerpt_tag.get_text(strip=True))
                excerpt = excerpt[:300]  # 限制长度

            # 提取作者（可选）
            author_tag = card.select_one('.AuthorInfo-name')
            author = author_tag.get_text(strip=True) if author_tag else "未知"

            if title and link:
                articles.append({
                    "title": title,
                    "link": link,
                    "excerpt": excerpt,
                    "author": author,
                })

        return articles

    def save_to_markdown(self, output_dir: str = "articles"):
        """将结果保存为 Markdown 文件"""
        os.makedirs(output_dir, exist_ok=True)

        # 先写汇总索引文件
        index_path = os.path.join(output_dir, "README.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"# 知乎「{self.keyword}」搜索结果汇总\n\n")
            f.write(f"> 共获取 {len(self.results)} 条结果\n\n")
            for idx, item in enumerate(self.results, 1):
                f.write(f"{idx}. [{item['title']}]({item['link']})\n")
                f.write(f"   - 作者: {item['author']}\n")
                f.write(f"   - 摘要: {item['excerpt'][:120]}...\n\n")

        # 每条结果单独保存
        for idx, item in enumerate(self.results, 1):
            filepath = os.path.join(output_dir, f"article_{idx:02d}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {item['title']}\n\n")
                f.write(f"- **来源**: [知乎]({item['link']})\n")
                f.write(f"- **作者**: {item['author']}\n")
                f.write(f"- **关键词**: {self.keyword}\n\n")
                f.write(f"## 摘要\n\n{item['excerpt']}\n\n")
                f.write("> 提示: 本文为搜索结果摘要，完整内容请访问原链接。\n"
                )

        print(f"[保存] 结果已写入 {output_dir}/ 目录")
        print(f"[保存] 汇总索引: {index_path}")

    def run(self):
        """主流程"""
        print(f"=== 知乎爬虫启动 | 关键词: {self.keyword} | 目标数量: {self.limit} ===")
        html = self.fetch_search_page()
        if not html:
            print("[退出] 未获取到页面内容")
            return

        if self._is_login_page(html):
            print("[警告] 检测到登录拦截，知乎可能要求登录才能查看完整搜索结果")
            print("[建议] 可尝试在浏览器登录知乎后，将 Cookie 填入 session 中再试")
            # 保存原始页面供调试
            debug_path = "debug_response.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html[:10000])
            print(f"[调试] 原始响应前10000字符已保存到 {debug_path}")
            return

        self.results = self.parse_results(html)
        print(f"[完成] 成功解析 {len(self.results)} 条结果")

        if self.results:
            self.save_to_markdown()
        else:
            print("[提示] 未解析出有效数据，建议检查 debug_response.html 或更换解析策略")


def main():
    scraper = ZhihuScraper(keyword="DeepSeek", limit=10)
    scraper.run()


if __name__ == "__main__":
    main()
