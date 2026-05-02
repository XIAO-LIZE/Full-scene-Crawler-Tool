"""
API爬虫 - 用于爬取REST API
"""
import logging
import json
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseSpider


logger = logging.getLogger(__name__)


class ApiSpider(BaseSpider):
    """API爬虫 - 用于爬取REST API"""
    
    def __init__(self, task, engine):
        super().__init__(task, engine)
        self.session = self._create_session()
        self._proxy_index = 0
    
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=self.task.spider_config.retry_times,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        headers.update(self.task.spider_config.headers)
        session.headers.update(headers)
        
        # 设置cookies
        if self.task.spider_config.cookies:
            session.cookies.update(self.task.spider_config.cookies)
        
        return session
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """获取代理配置"""
        if not self.task.proxy_config.enabled:
            return None
        
        if self.task.proxy_config.rotation and self.task.proxy_config.proxy_list:
            # 轮换代理
            proxy = self.task.proxy_config.proxy_list[self._proxy_index % len(self.task.proxy_config.proxy_list)]
            self._proxy_index += 1
            return {"http": proxy, "https": proxy}
        else:
            # 固定代理
            proxies = {}
            if self.task.proxy_config.http_proxy:
                proxies["http"] = self.task.proxy_config.http_proxy
            if self.task.proxy_config.https_proxy:
                proxies["https"] = self.task.proxy_config.https_proxy
            return proxies if proxies else None
    
    def _login(self):
        """执行登录"""
        if not self.task.login_config.login_url:
            return
        
        try:
            login_data = {
                self.task.login_config.username_field: self.task.login_config.username,
                self.task.login_config.password_field: self.task.login_config.password,
            }
            
            headers = self.task.spider_config.headers.copy()
            headers.update(self.task.login_config.headers)
            
            response = self.session.post(
                self.task.login_config.login_url,
                json=login_data,
                headers=headers,
                timeout=self.task.spider_config.timeout,
            )
            
            if response.status_code == 200:
                # 尝试从响应中提取token
                try:
                    data = response.json()
                    if "token" in data:
                        self.session.headers["Authorization"] = f"Bearer {data['token']}"
                    elif "access_token" in data:
                        self.session.headers["Authorization"] = f"Bearer {data['access_token']}"
                except:
                    pass
                
                # 更新cookies
                self.task.spider_config.cookies.update(dict(response.cookies))
                logger.info("Login successful")
            else:
                logger.warning(f"Login failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取API响应"""
        for attempt in range(self.task.spider_config.retry_times + 1):
            try:
                proxies = self._get_proxy()
                
                # 判断请求方法
                method = self.task.metadata.get("api_method", "GET").upper()
                
                if method == "GET":
                    response = self.session.get(
                        url,
                        params=self.task.metadata.get("api_params"),
                        headers=self.task.spider_config.headers,
                        cookies=self.task.spider_config.cookies,
                        proxies=proxies,
                        timeout=self.task.spider_config.timeout,
                    )
                elif method == "POST":
                    response = self.session.post(
                        url,
                        json=self.task.metadata.get("api_data"),
                        params=self.task.metadata.get("api_params"),
                        headers=self.task.spider_config.headers,
                        cookies=self.task.spider_config.cookies,
                        proxies=proxies,
                        timeout=self.task.spider_config.timeout,
                    )
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                response.raise_for_status()
                
                # 返回JSON字符串
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}): {url} - {e}")
                if attempt < self.task.spider_config.retry_times:
                    import time
                    time.sleep(self.task.spider_config.retry_delay)
                else:
                    logger.error(f"Failed to fetch API after {self.task.spider_config.retry_times + 1} attempts: {url}")
                    return None
    
    def _parse_page(self, url: str, html: str, depth: int, parent_url: str):
        """解析API响应"""
        try:
            # 尝试解析JSON
            data = json.loads(html)
            
            # 如果有解析规则，应用它们
            if self.task.parse_rules:
                parsed_data = {}
                for rule in self.task.parse_rules:
                    value = self._extract_json_value(data, rule)
                    parsed_data[rule.name] = value
                data = parsed_data
            
            from ...models.result import ScrapedItem
            import uuid
            
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
            
        except json.JSONDecodeError:
            # 如果不是JSON，回退到HTML解析
            return super()._parse_page(url, html, depth, parent_url)
    
    def _extract_json_value(self, data: Any, rule) -> Any:
        """从JSON数据中提取值"""
        try:
            # 支持点号分隔的路径，如 "data.items[0].name"
            path = rule.selector.split(".")
            current = data
            
            for key in path:
                if "[" in key and "]" in key:
                    # 处理数组索引
                    array_key = key.split("[")[0]
                    index = int(key.split("[")[1].split("]")[0])
                    if array_key:
                        current = current[array_key]
                    current = current[index]
                else:
                    current = current[key]
            
            return current if current is not None else rule.default_value
            
        except (KeyError, IndexError, TypeError, ValueError):
            return rule.default_value
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()