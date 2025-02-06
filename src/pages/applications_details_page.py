from src.logger import logger
from selenium.webdriver.common.by import By
from src.webdriver_manager_c import WebDriverManager


class ApplicationDetailPage:
    def __init__(self, driver_manager: WebDriverManager):
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()

    def get_background_verification_status(self):

        self.choose_primary_applicant()

        last_activity_status = ''
        try:
            background_check = self.driver_manager.wait_for_element(
                By.XPATH, "//div[contains(@class, 'chip-container')]//p[text()='In progress']", timeout=15
            ).text

            last_activity_status += f"background check - {background_check.lower()}\n"

            activities = self.driver_manager.wait_for_elements(By.CLASS_NAME, "activity", timeout=10)

            if activities:
                last_activity_raw = activities[0].find_element(By.CLASS_NAME, "date")
                last_activity_date = last_activity_raw.text.strip()
                last_activity_status += f"last app update - {last_activity_date}\n"
                return last_activity_status
        except Exception as e:
            print("Error retrieving last activity date:", e)
        return None

    def choose_primary_applicant(self):
        primary_applicant_app_link = self.driver_manager.wait_for_element(By.CLASS_NAME, "full-app-link")
        primary_applicant_app_link.click()
