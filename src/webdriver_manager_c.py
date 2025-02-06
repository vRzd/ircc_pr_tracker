from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from src.logger import logger

class WebDriverManager:
    def __init__(self, config):
        self._timeout = 10
        self.headless = config["webdriver"].get("headless", True)
        self.driver = None

    def get_driver(self):
        if not self.driver:
            options = self._get_chrome_options()
            # driver_path = ChromeDriverManager().install()
            driver_path = "/Users/vdrozd/.wdm/drivers/chromedriver/mac64/132.0.6834.159/chromedriver-mac-arm64/chromedriver"
            logger.info(f"Using Chromedriver from: {driver_path}")
            self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        return self.driver

    def _get_chrome_options(self):
        options = Options()
        if self.headless:
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
            )
        return options

    def open_url(self, url):
        self.driver.get(url)

    def wait_for_element(self, by, value, timeout=None):
        timeout = timeout or self._timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_elements(self, by, value, timeout=None):
        timeout = timeout or self._timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def click(self, by, value, timeout=None):
        try:
            timeout = timeout or self._timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value)))
            element.click()
            logger.debug(f"Clicked element: {value}")
        except Exception as e:
            logger.warning(f"Normal click failed for {value}.")

    def type(self, by, value, keys, timeout=None):
        timeout = timeout or self._timeout
        element = self.wait_for_element(by, value, timeout)
        self.send_keys(element, keys)

    def select_dropdown_option(self, dropdown_id, option_css, timeout=None):
        timeout = timeout or self._timeout
        dropdown = self.wait_for_element(By.ID, dropdown_id, timeout)
        self._scroll_into_view(dropdown)
        dropdown.click()
        option = self.wait_for_element(By.CSS_SELECTOR, option_css, timeout)
        self._scroll_into_view(option)
        option.click()

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def press_key(self, element_id, key, timeout=None):
        timeout = timeout or self._timeout
        try:
            element = self.wait_for_element(By.ID, element_id, timeout)
            element.send_keys(key)
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error: Unable to locate element {element_id}. Exception: {e}")

    @staticmethod
    def send_keys(element, keys):
        element.clear()
        element.send_keys(keys)

    def _scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
