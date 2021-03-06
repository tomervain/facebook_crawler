import time
from dataclasses import dataclass

from selenium.webdriver.chrome.webdriver import WebDriver
from lib.config.locators import facebook_page_loc as fpl
from lib.config.strings import FACEBOOK_PAGE_MAIN


@dataclass
class ScrapePageData:
    """Task for scraping Facebook's page Data"""
    driver: WebDriver
    username: str
    time: int = 0
    likes_followers: tuple = None

    def run(self):
        """runs the task and update attributes"""
        self.time = time.perf_counter()
        self.driver.implicitly_wait(3)
        self.driver.get(FACEBOOK_PAGE_MAIN % self.username)
        about = self.driver.find_elements_by_css_selector(fpl['ABOUT'])
        about = [s.text.split()[0].replace(',','') for s in about]
        about = list(filter(lambda s: s.isnumeric(), about))
        self.likes_followers = tuple(int(s) for s in about)
        self.time = time.perf_counter() - self.time
