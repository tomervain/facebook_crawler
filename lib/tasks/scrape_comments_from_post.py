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
from selenium.common.exceptions import TimeoutException

from lib.config.locators import comments_page_loc as cpl
from lib.config.strings import POST_PAGE, CLEAR_ITEMS
from lib.models.post import Post
from lib.models.comment import Comment


@dataclass
class ScrapeCommentsFromPost:
    """Task for scraping all comments from a single facebook post"""
    driver: WebDriver
    post: Post
    time: int = 0
    scraped_comments: List[Comment] = field(default_factory=list)
    date_prediction: bool = True

    @staticmethod
    def _more_button_clickable():
        return ec.element_to_be_clickable((By.CSS_SELECTOR, cpl['MORE_COMMENTS']))

    @staticmethod
    def _presence_of_all_comments():
        return ec.presence_of_all_elements_located((By.CSS_SELECTOR, cpl['COMMENTS']))

    @staticmethod
    def _wait_time_update(wait_time: int, measured_time: float):
        return wait_time*2 if measured_time/wait_time >= .7 else wait_time

    def _append_comment(self, comment: WebElement):
        self.scraped_comments.append(Comment(
            element=comment,
            pagename=self.post.pagename))

    def run(self):
        """runs the task and save scraped comments in list"""
        self.driver.get(POST_PAGE % self.post.post_id)
        comments = self.driver.find_elements_by_css_selector(cpl['COMMENTS'])
        for comment in comments:
            self._append_comment(comment)
        self.driver.execute_script(CLEAR_ITEMS % cpl['COMMENTS'])

        more_button = self.driver.find_elements_by_css_selector(
            cpl['MORE_COMMENTS'])
        if more_button:
            more_button[0].click()
            try:
                wait_time = 15  # initial waiting time
                wait = WebDriverWait(self.driver, wait_time)
                comments = wait.until(self._presence_of_all_comments())
                while comments:
                    for comment in comments:
                        self._append_comment(comment)
                    self.driver.execute_script(CLEAR_ITEMS % cpl['COMMENTS'])
                    wait = WebDriverWait(self.driver, 10)
                    more_button = wait.until(self._more_button_clickable())
                    more_button.click()
                    timer = time.monotonic()
                    wait = WebDriverWait(self.driver, wait_time)
                    comments = wait.until(self._presence_of_all_comments())
                    timer = time.monotonic() - timer
                    wait_time = self._wait_time_update(wait_time, timer)
            except TimeoutException:
                print('reached timeout, terminate loop')
