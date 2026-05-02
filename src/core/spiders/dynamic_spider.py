"""
动态页面爬虫 - 使用Selenium
"""
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .base import BaseSpider


logger = logging.getLogger(__name__)


class DynamicSpider(BaseSpider):
    """动态页面爬虫 - 使用Selenium"""
    
    def __init__(self, task, engine):
        super().__init__(task, engine)
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """初始化WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 设置User-Agent
            if self.task.spider_config.headers.get("User-Agent"):
                chrome_options.add_argument(f"--user-agent={self.task.spider_config.headers['User-Agent']}")
            
            # 设置代理
            if self.task.proxy_config.enabled:
                if self.task.proxy_config.http_proxy:
                    chrome_options.add_argument(f"--proxy-server={self.task.proxy_config.http_proxy}")
            
            # 尝试初始化Chrome驱动
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except WebDriverException:
                # 如果Chrome不可用，尝试使用Firefox
                logger.warning("Chrome driver not available, trying Firefox...")
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=firefox_options)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(self.task.spider_config.timeout)
            
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _login(self):
        """执行登录"""
        if not self.task.login_config.login_url:
            return
        
        try:
            self.driver.get(self.task.login_config.login_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, self.task.spider_config.timeout).until(
                EC.presence_of_element_located((By.NAME, self.task.login_config.username_field))
            )
            
            # 输入用户名和密码
            username_input = self.driver.find_element(By.NAME, self.task.login_config.username_field)
            password_input = self.driver.find_element(By.NAME, self.task.login_config.password_field)
            
            username_input.send_keys(self.task.login_config.username)
            password_input.send_keys(self.task.login_config.password)
            
            # 提交表单（尝试多种方式）
            try:
                # 尝试点击提交按钮
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                submit_button.click()
            except:
                # 尝试按回车键
                from selenium.webdriver.common.keys import Keys
                password_input.send_keys(Keys.RETURN)
            
            # 等待登录完成
            import time
            time.sleep(2)
            
            # 获取cookies
            cookies = self.driver.get_cookies()
            self.task.spider_config.cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            
            logger.info("Login successful")
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
    
    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(self.task.spider_config.retry_times + 1):
            try:
                self.driver.get(url)
                
                # 等待页面加载完成
                WebDriverWait(self.driver, self.task.spider_config.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 可以添加自定义等待条件
                # 例如等待特定元素出现
                # WebDriverWait(self.driver, self.task.spider_config.timeout).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, ".content"))
                # )
                
                # 额外等待JavaScript执行
                import time
                time.sleep(1)
                
                return self.driver.page_source
                
            except TimeoutException:
                logger.warning(f"Page load timeout (attempt {attempt + 1}): {url}")
                if attempt < self.task.spider_config.retry_times:
                    import time
                    time.sleep(self.task.spider_config.retry_delay)
                else:
                    logger.error(f"Failed to fetch page after timeout: {url}")
                    return None
                    
            except WebDriverException as e:
                logger.warning(f"WebDriver error (attempt {attempt + 1}): {url} - {e}")
                if attempt < self.task.spider_config.retry_times:
                    import time
                    time.sleep(self.task.spider_config.retry_delay)
                else:
                    logger.error(f"Failed to fetch page: {url}")
                    return None
    
    def close(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")