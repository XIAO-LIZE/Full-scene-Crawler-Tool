"""
基础爬虫类
"""
import time
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from bs4 import BeautifulSoup

from ...models.task import SpiderTask, SpiderType
from ...models.result import TaskResult, ScrapedItem


logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, task: SpiderTask, engine):
        self.task = task
        self.engine = engine
        self.result = TaskResult(task_id=task.task_id)
        self._stopped = False
    
    @abstractmethod
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭资源"""
        pass
    
    def run(self) -> TaskResult:
        """运行爬虫"""
        logger.info(f"Starting spider for task: {self.task.task_id}")
        self.result.started_at = datetime.now()
        
        try:
            # 如果需要登录，先执行登录
            if self.task.login_config.enabled:
                self._login()
            
            # 爬取起始URL
            for url in self.task.spider_config.start_urls:
                if self._stopped:
                    break
                
                self._crawl_url(url, depth=0)
            
            self.result.complete()
            logger.info(f"Spider completed: {self.task.task_id}")
            
        except Exception as e:
            logger.exception(f"Spider failed: {self.task.task_id}")
            self.result.set_error(str(e))
        
        finally:
            self.close()
        
        return self.result
    
    def _login(self):
        """执行登录（子类可重写）"""
        pass
    
    def _crawl_url(self, url: str, depth: int = 0, parent_url: str = ""):
        """爬取单个URL"""
        if self._stopped:
            return
        
        # 检查深度限制
        if depth > self.task.spider_config.max_depth:
            return
        
        # 检查域名限制
        if self.task.spider_config.allowed_domains:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain not in self.task.spider_config.allowed_domains:
                logger.debug(f"Skipping URL (domain not allowed): {url}")
                return
        
        # 请求延迟
        if depth > 0 and self.task.spider_config.delay_between_requests > 0:
            time.sleep(self.task.spider_config.delay_between_requests)
        
        logger.info(f"Crawling URL: {url} (depth: {depth})")
        
        # 获取页面内容
        html = self.fetch_page(url)
        if not html:
            self.result.items_failed += 1
            return
        
        # 通知引擎页面已爬取
        self.engine.on_page_crawled(self.task, url)
        
        # 解析页面
        item = self._parse_page(url, html, depth, parent_url)
        if item:
            # 通知引擎数据项已爬取
            self.engine.on_item_scraped(self.task, item)
        
        # 如果需要跟踪链接，提取并爬取链接
        if self.task.spider_config.follow_links and depth < self.task.spider_config.max_depth:
            links = self._extract_links(html, url)
            for link in links:
                if self._stopped:
                    break
                self._crawl_url(link, depth + 1, url)
    
    def _parse_page(self, url: str, html: str, depth: int, parent_url: str) -> Optional[ScrapedItem]:
        """解析页面"""
        try:
            soup = BeautifulSoup(html, "lxml")
            data = {}
            
            for rule in self.task.parse_rules:
                value = self._extract_value(soup, rule)
                data[rule.name] = value
            
            item = ScrapedItem(
                item_id=str(uuid.uuid4())[:8],
                task_id=self.task.task_id,
                url=url,
                data=data,
                raw_html=html if self.task.metadata.get("save_raw_html", False) else "",
                depth=depth,
                parent_url=parent_url,
            )
            
            return item
            
        except Exception as e:
            logger.error(f"Failed to parse page {url}: {e}")
            return None
    
    def _extract_value(self, soup: BeautifulSoup, rule) -> Any:
        """根据规则提取值"""
        try:
            if rule.selector_type == "css":
                elements = soup.select(rule.selector)
            elif rule.selector_type == "xpath":
                # 使用lxml的xpath
                from lxml import etree
                tree = etree.HTML(str(soup))
                elements = tree.xpath(rule.selector)
            elif rule.selector_type == "regex":
                import re
                match = re.search(rule.selector, str(soup))
                return match.group(0) if match else rule.default_value
            else:
                return rule.default_value
            
            if not elements:
                return rule.default_value
            
            # 提取属性
            if rule.selector_type == "xpath":
                # xpath返回的是元素列表或字符串
                if isinstance(elements, list):
                    if len(elements) > 0:
                        if rule.attribute == "text":
                            return elements[0].text if hasattr(elements[0], "text") else str(elements[0])
                        else:
                            return elements[0].get(rule.attribute, rule.default_value)
                return str(elements) if elements else rule.default_value
            else:
                # CSS选择器
                element = elements[0]
                if rule.attribute == "text":
                    value = element.get_text(strip=True)
                elif rule.attribute == "html":
                    value = str(element)
                else:
                    value = element.get(rule.attribute, rule.default_value)
                
                # 后处理
                if rule.post_process:
                    value = self._post_process(value, rule.post_process)
                
                return value
                
        except Exception as e:
            logger.error(f"Failed to extract value for rule {rule.name}: {e}")
            return rule.default_value
    
    def _post_process(self, value: Any, process_name: str) -> Any:
        """后处理函数"""
        if process_name == "strip":
            return str(value).strip()
        elif process_name == "lower":
            return str(value).lower()
        elif process_name == "upper":
            return str(value).upper()
        elif process_name == "int":
            try:
                return int(str(value).strip())
            except:
                return 0
        elif process_name == "float":
            try:
                return float(str(value).strip())
            except:
                return 0.0
        elif process_name == "clean_whitespace":
            import re
            return re.sub(r'\s+', ' ', str(value)).strip()
        else:
            return value
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """提取页面中的链接"""
        try:
            from urllib.parse import urljoin, urlparse
            import re
            
            soup = BeautifulSoup(html, "lxml")
            links = []
            
            # 提取所有a标签的href
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                # 转换为绝对URL
                absolute_url = urljoin(base_url, href)
                
                # 过滤掉锚点和javascript
                if absolute_url.startswith(("http://", "https://")):
                    # 如果有正则表达式过滤
                    if self.task.spider_config.link_extractor_regex:
                        if re.match(self.task.spider_config.link_extractor_regex, absolute_url):
                            links.append(absolute_url)
                    else:
                        links.append(absolute_url)
            
            # 去重
            return list(set(links))
            
        except Exception as e:
            logger.error(f"Failed to extract links: {e}")
            return []
    
    def stop(self):
        """停止爬虫"""
        self._stopped = True