import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List
from numpy import polyfit, polyval
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from lib.config.locators import comments_page_loc as cpl
from lib.config.locators import comments_regular_loc as crl
from lib.config.strings import POST_PAGE, POST_REGULAR, CLEAR_ITEMS, LEAVE_MAIN_POST
from lib.models.post import Post
from lib.models.comment import Comment


@dataclass
class ScrapeCommentsFromPost:
    """Task for scraping all comments from a single facebook post"""
    driver: WebDriver
    post: Post
    time: int = 0
    scraped_comments: List[Comment] = field(default_factory=list)
    include_dates: bool = True

    @staticmethod
    def _more_button_clickable():
        return ec.element_to_be_clickable((By.CSS_SELECTOR, cpl['MORE_COMMENTS']))

    @staticmethod
    def _presence_of_all_comments():
        return ec.presence_of_all_elements_located((By.CSS_SELECTOR, cpl['COMMENTS']))

    @staticmethod
    def _presence_of_other_posts():
        return ec.presence_of_all_elements_located((By.CSS_SELECTOR, crl['OTHERS']))

    @staticmethod
    def _show_button_clickable():
        return ec.element_to_be_clickable((By.CSS_SELECTOR, crl['SHOW_MORE']))

    @staticmethod
    def _visibility_of_all_comments():
        return ec.visibility_of_all_elements_located((By.CSS_SELECTOR, crl['COMMENTS']))

    @staticmethod
    def _tooltip_visible():
        return ec.visibility_of_element_located((By.CSS_SELECTOR, crl['TOOLTIP']))

    @staticmethod
    def _wait_time_update(wait_time: int, measured_time: float):
        return wait_time*2 if measured_time/wait_time >= .7 else wait_time

    @staticmethod
    def _parse_datetime(time_string: str) -> datetime:
        try:
            prefix = time_string.split()[0]
            # case 1: "Today at HH:MM"
            if prefix == 'Today':
                ctime = ' '.join(time_string.split()[2:])
                ctime = datetime.strptime(ctime, "%H:%M")
                year, month, day = datetime.today().timetuple()[:3]
                hour, minute = ctime.timetuple()[3:5]
            # case 2: "Yesterday at HH:MM"
            elif prefix == 'Yesterday':
                yday = datetime.today() - timedelta(1)
                ctime = ' '.join(time_string.split()[2:])
                ctime = datetime.strptime(ctime, "%H:%M")
                year, month, day = yday.timetuple()[:3]
                hour, minute = ctime.timetuple()[3:5]
            # case 3: "Month Day at HH:MM"
            else:
                cdt = datetime.strptime(time_string, "%d %B at %H:%M")
                year = datetime.today().year
                month, day, hour, minute = cdt.timetuple()[1:5]

            return datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        except:
            return None

    def _date_estimator(self, cid_date_dict: dict) -> list:
        delta = list(map(lambda cid: abs(cid - self.post.post_id),
                         cid_date_dict.keys()))
        timestamp = list(map(lambda dtime: dtime.timestamp(),
                             cid_date_dict.values()))
        return polyfit(delta, timestamp, 1)

    def _data_from_timetag(self, comment: WebElement):
        # move to anchor
        anchor = comment.find_element_by_css_selector(crl['ANCHOR'])
        webdriver.ActionChains(self.driver).move_to_element(anchor).perform()

        # move to timetag and hover
        timetag = comment.find_element_by_css_selector(crl['TIMETAG'])
        href = timetag.get_attribute('href')
        webdriver.ActionChains(self.driver).move_to_element(timetag).perform()
        wait = WebDriverWait(self.driver, 30)
        tooltip = wait.until(self._tooltip_visible())

        return href, tooltip

    def _append_comment(self, comment: WebElement):
        self.scraped_comments.append(Comment(
            element=comment,
            pagename=self.post.pagename))

    def _scrape_dates_from_regular_post(self) -> dict:
        cid_date_dict = {}
        self.driver.get(POST_REGULAR %
                        (self.post.username, self.post.post_id))
        wait = WebDriverWait(self.driver, 30)
        wait.until(self._presence_of_other_posts())
        self.driver.execute_script(LEAVE_MAIN_POST)

        # attempt expanding comments if there are more comments to show
        if self.driver.find_elements_by_css_selector(crl['SHOW_MORE']):
            wait = WebDriverWait(self.driver, 20)
            show_button = wait.until(self._show_button_clickable())
            webdriver.ActionChains(self.driver).double_click(
                show_button).perform()

        wait = WebDriverWait(self.driver, 30)
        wait.until(self._visibility_of_all_comments())
        self.driver.execute_script(CLEAR_ITEMS % crl['COMMENT_CONTENT'])
        self.driver.execute_script(CLEAR_ITEMS % crl['REACTION_TAGS'])
        comments = self.driver.find_elements_by_css_selector(crl['COMMENTS'])
        for comment in comments:
            href, tooltip = self._data_from_timetag(comment)
            comment_id = re.search(r'(?<=comment_id=).*?(?=&)', href).group()
            comment_datetime = self._parse_datetime(tooltip.text)
            cid_date_dict[int(comment_id)] = comment_datetime
        return cid_date_dict

    def run(self):
        """runs the task and save scraped comments in list"""
        self.time = time.perf_counter()
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
                pass

        # datetime scraping and update
        if self.include_dates:
            cid_date_dict = self._scrape_dates_from_regular_post()
            coeff = self._date_estimator(cid_date_dict)
            for comment in self.scraped_comments:
                delta = abs(comment.comment_id - self.post.post_id)
                timestamp = polyval(coeff, delta)
                comment.parse_datetime(cid_date_dict, timestamp)

        self.time = time.perf_counter() - self.time
