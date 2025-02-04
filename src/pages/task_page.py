from src.logger import logger
from selenium.webdriver.common.by import By
from src.webdriver_manager_c import WebDriverManager


class TaskPage:
    def __init__(self, driver_manager: WebDriverManager):
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()

    def get_task_count(self):
        try:
            task_elements = self.driver_manager.wait_for_elements(By.CLASS_NAME, "apps-task")
            task_count = 0
            for element in task_elements:
                task_text = element.text.strip()
                try:
                    task_count += int(task_text.split()[0])
                except (ValueError, IndexError):
                    logger.warning(f"Error parsing task text: '{task_text}'")

            logger.info(f"Task count retrieved: {task_count}")
            return task_count
        except Exception as e:
            logger.error("Error retrieving tasks:", exc_info=True)
            return None
