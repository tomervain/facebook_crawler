from selenium.webdriver.chrome.webdriver import WebDriver
from lib.config.locators import facebook_page_loc as fpl
from lib.config.strings import FACEBOOK_PAGE_URL


class ScrapePageData:
    """Task for scraping Facebook's page Data"""

    def __init__(self, driver: WebDriver, username: str):
        self.driver = driver
        self.username = username
        self.time = int()
        self.likes_followers = tuple()

    def execute(self):
        """executes the task and update attributes"""
        self.driver.implicitly_wait(3)
        self.driver.get(FACEBOOK_PAGE_URL % self.username)
        about = self.driver.find_elements_by_css_selector(fpl['ABOUT'])
        print(about[2].text)
