from selenium import webdriver
from src.logger import logger
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebDriverManager:
    def __init__(self, config):
        self.headless = config["webdriver"].get("headless", True)
        self.driver = None

    def get_driver(self):
        if not self.driver:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
            )

            self.driver = webdriver.Chrome(service=Service(), options=options)
        return self.driver

    def open_url(self, url):
        self.driver.get(url)

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def click(self, by, value, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()

    def type(self, by, value, keys, timeout=10):
        element = self.wait_for_element(by, value, timeout)
        element.clear()
        element.send_keys(keys)

    def select_dropdown_option(self, dropdown_id, option_css, timeout=5):
        dropdown = self.wait_for_element(By.ID, dropdown_id, timeout)
        dropdown.click()
        option = self.wait_for_element(By.CSS_SELECTOR, option_css, timeout)
        option.click()

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    @staticmethod
    def send_keys(element, keys):
        element.clear()
        element.send_keys(keys)