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
from lib.config.strings import FACEBOOK_PAGE_POSTS, WTO_POSTS_VISIBLE
from lib.models.page import Page
from lib.models.post import Post


@dataclass
class ScrapePostsFromPage:
    """Task for scraping posts from a single facebook page"""
    driver: WebDriver
    page: Page
    time: int = 0
    scraped_posts: List[Post] = field(default_factory=list)
    include_reactions: bool = True

    @staticmethod
    def _posts_are_visible():
        return ec.visibility_of_all_elements_located((By.CSS_SELECTOR, ppl['POSTS']))

    @staticmethod
    def _get_post_date(element: WebElement) -> date:
        data_string = element.get_attribute('data-store')
        timestamp = re.search(
            r'(?<=\\\"publish_time\\\":).*?(?=,)', data_string).group()
        return datetime.fromtimestamp(int(timestamp)).date()

    @staticmethod
    def _is_live_now(post: WebElement) -> bool:
        header = post.find_element_by_css_selector(ppl['POST_HEADER'])
        return 'live now' not in header.text.lower()

    def _scroll_down(self):
        webdriver.ActionChains(self.driver).send_keys(Keys.END).perform()
        time.sleep(1)  # minor delay for optimization

    def _filter_posts(self, posts: List[WebElement], threshold: date) -> List[WebElement]:
        # ? is the first post "pinned" and below threshold?
        if self._get_post_date(posts[0]) < threshold:
            posts.pop(0)

        # iterate backwards, removing all posts below threshold
        while self._get_post_date(posts[-1]) < threshold:
            posts.pop(-1)

        return list(filter(self._is_live_now, posts))

    def run(self, threshold: int = 3):
        """runs the task and save scraped posts in list

        Args:
            threshold (int, optional): Amount of days a post goes back. Defaults to 3.
        """
        self.time = time.perf_counter()
        date_threshold = date.today() - timedelta(threshold)
        last_date = date.today()
        self.driver.get(FACEBOOK_PAGE_POSTS % self.page.username)

        while last_date >= date_threshold:
            self._scroll_down()
            wait = WebDriverWait(self.driver, 10)
            posts = wait.until(self._posts_are_visible(), WTO_POSTS_VISIBLE)
            last_date = self._get_post_date(posts[-1])

        posts = self._filter_posts(posts, date_threshold)
        for post in posts:
            webdriver.ActionChains(self.driver).move_to_element(post).perform()
            self.scraped_posts.append(Post(
                driver=self.driver,
                element=post,
                page=self.page,
                include_reactions=self.include_reactions))

        self.time = time.perf_counter() - self.time
