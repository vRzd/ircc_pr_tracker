from src.logger import logger
from selenium.webdriver.common.by import By


class ProcessingTimePage:
    def __init__(self, driver_manager, config):
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()
        self.url = config.get("processing_time_url")

    def get_processing_time(self):
        try:
            self.driver.get(self.url)
            logger.info(f"Navigated to processing time page: {self.url}")

            self.driver_manager.wait_for_element(By.ID, "wb-auto-24")

            self.driver_manager.select_dropdown_option("wb-auto-24", "#wb-auto-24 > option:nth-child(3)")
            self.driver_manager.select_dropdown_option("wb-auto-43", "#wb-auto-43 > option:nth-child(5)")
            self.driver_manager.select_dropdown_option("wb-auto-46", "#wb-auto-46 > option:nth-child(3)")

            self.driver_manager.click(By.CSS_SELECTOR, ".btn-call-to-action")

            avg_month = self.driver_manager.wait_for_element(By.ID, "wb-auto-48").text

            logger.info(f"Processing time retrieved: {avg_month}")
            return f"avg processing time - {avg_month}"
        except Exception as e:
            logger.error("Error checking processing time:", exc_info=True)
            return "avg processing time - is unavailable"
