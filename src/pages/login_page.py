from src.logger import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.webdriver_manager import WebDriverManager


class LoginPage:
    def __init__(self, driver_manager: WebDriverManager, config):
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()
        self.config = config

    def login(self):
        try:
            self.driver_manager.open_url(self.config["login_url"])
            logger.info(f"Navigating to login page: {self.config['login_url']}")

            self.driver_manager.type(By.ID, "uci", self.config["uci"])
            self.driver_manager.type(By.ID, "password", self.config["password"])
            self.driver_manager.type(By.ID, "password", Keys.RETURN)

            logger.info("Login successful.")
        except Exception as e:
            logger.error("Login failed:", exc_info=True)
