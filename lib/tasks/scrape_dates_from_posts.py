import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from lib.config.locators import posts_page_loc as ppl
from lib.config.strings import FACEBOOK_PAGE_POSTS, WTO_POSTS_VISIBLE, CLEAR_ITEMS
from lib.models.page import Page
from lib.models.post import Post


@dataclass
class ScrapeDatesFromPosts:
    """Task for scraping date tags from posts section"""
    driver: WebDriver
    page: Page
    time: int = 0
    date_dict: dict = field(default_factory=dict)

    @staticmethod
    def _posts_are_visible():
        return ec.visibility_of_all_elements_located((By.CSS_SELECTOR, ppl['POSTS']))

    def _scroll_down(self):
        webdriver.ActionChains(self.driver).send_keys(Keys.END).perform()
        time.sleep(1)  # minor delay for optimization

    @staticmethod
    def _get_post_date(element: WebElement) -> date:
        data_string = element.get_attribute('data-store')
        timestamp = re.search(
            r'(?<=\\\"publish_time\\\":).*?(?=,)', data_string).group()
        return datetime.fromtimestamp(int(timestamp)).date()

    @staticmethod
    def _get_post_data(element: WebElement) -> tuple:
        data_string = element.get_attribute('data-store')
        timestamp = re.search(r'(?<=\\\"publish_time\\\":).*?(?=,)', data_string)
        dtime = int(timestamp.group())
        post_id = int(re.search(r'(?<=post_id\.).*?(?=:)', data_string).group())
        return post_id, dtime


    def run(self, threshold: int = 3):
        """runs the task and save post's id and dates in dictionary

        Args:
            threshold (int, optional): Amount of days a post goes back. Defaults to 3.
        """
        self.time = time.perf_counter()
        date_threshold = date.today() - timedelta(threshold)
        last_date = date.today()
        self.driver.get(FACEBOOK_PAGE_POSTS % self.page.username)
        self.driver.execute_script(CLEAR_ITEMS % ppl['SIGN_HEADER'])

        while last_date >= date_threshold:
            self._scroll_down()
            wait = WebDriverWait(self.driver, 10)
            posts = wait.until(self._posts_are_visible(), WTO_POSTS_VISIBLE)
            last_date = self._get_post_date(posts[-1])

        for post in posts:
            webdriver.ActionChains(self.driver).move_to_element(post).perform()
            post_id, post_dt = self._get_post_data(post)
            self.date_dict[post_id] = post_dt

        self.time = time.perf_counter() - self.time