"""
静态页面爬虫
"""
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseSpider


logger = logging.getLogger(__name__)


class StaticSpider(BaseSpider):
    """静态页面爬虫 - 使用requests库"""
    
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
        if self.task.spider_config.headers:
            session.headers.update(self.task.spider_config.headers)
        
        # 设置cookies
        if self.task.spider_config.cookies:
            session.cookies.update(self.task.spider_config.cookies)
        
        # 设置超时
        session.timeout = self.task.spider_config.timeout
        
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
            
            # 合并额外的headers
            headers = self.task.spider_config.headers.copy()
            headers.update(self.task.login_config.headers)
            
            response = self.session.post(
                self.task.login_config.login_url,
                data=login_data,
                headers=headers,
                timeout=self.task.spider_config.timeout,
            )
            
            if response.status_code == 200:
                logger.info("Login successful")
                # 更新cookies
                self.task.spider_config.cookies.update(dict(response.cookies))
            else:
                logger.warning(f"Login failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(self.task.spider_config.retry_times + 1):
            try:
                proxies = self._get_proxy()
                
                response = self.session.get(
                    url,
                    headers=self.task.spider_config.headers,
                    cookies=self.task.spider_config.cookies,
                    proxies=proxies,
                    timeout=self.task.spider_config.timeout,
                )
                
                response.raise_for_status()
                
                # 检测编码
                if response.encoding:
                    response.encoding = response.apparent_encoding
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {url} - {e}")
                if attempt < self.task.spider_config.retry_times:
                    import time
                    time.sleep(self.task.spider_config.retry_delay)
                else:
                    logger.error(f"Failed to fetch page after {self.task.spider_config.retry_times + 1} attempts: {url}")
                    return None
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()