import re
import time
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from lib.config.locators import post_loc as pl
from lib.config.strings import POST_REACTIONS
from lib.models.page import Page


@dataclass
class Post:
    """Holds data of scraped Facebook post."""
    driver: InitVar[WebDriver]
    element: InitVar[WebElement]
    page: InitVar[Page]
    include_reactions: InitVar[bool]
    post_id: int = field(init=False)
    datetime: str = field(init=False)

    def __post_init__(self, driver, element, page, include_reactions):
        self.pagename = page.fullname
        self.username = page.username
        self.type = self._parse_type(element)
        self.post_id = self._parse_id(element)
        self.datetime = self._parse_datetime(element)
        self.comments = self._parse_comments(element)
        self.shares = self._parse_shares(element)
        self.content = self._parse_content(element)

        text, mentions = self._parse_text(driver, element)
        self.text = text
        self.mentions = mentions

        if include_reactions:
            self.reactions = self._parse_reactions(driver, element, self.post_id)


    @staticmethod
    def _parse_type(element: WebElement) -> str:
        header = element.find_element_by_css_selector(pl['HEADER'])
        return 'live post' if 'live' in header.text.lower() else 'post'

    @staticmethod
    def _parse_id(element: WebElement) -> int:
        data = element.get_attribute('data-store')
        post_id = re.search(r'(?<=post_id\.).*?(?=:)', data)
        return int(post_id.group())

    @staticmethod
    def _parse_datetime(element: WebElement) -> str:
        data = element.get_attribute('data-store')
        timestamp = re.search(r'(?<=\\\"publish_time\\\":).*?(?=,)', data)
        dtime = datetime.fromtimestamp(int(timestamp.group()))
        return dtime.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _parse_comments(element: WebElement) -> int:
        comments = element.find_elements_by_css_selector(pl['COMMENTS'])
        if comments:
            comm_str = comments[0].text.split()[0].upper()
            if comm_str[-1] == 'K':
                count = int(float(comm_str[:-1])*1e3)
            else:
                count = int(comm_str)
            return count
        return 0

    @staticmethod
    def _parse_shares(element: WebElement) -> int:
        shares = element.find_elements_by_css_selector(pl['SHARES'])
        if shares:
            share_str = shares[0].text.split()[0].upper()
            if share_str[-1] == 'K':
                count = int(float(share_str[:-1])*1e3)
            else:
                count = int(share_str)
            return count
        return 0

    @staticmethod
    def _parse_content(element: WebElement) -> str:
        post_share = element.find_elements_by_css_selector(pl['POST_SHARE'])
        if post_share:
            metadata = post_share[0].get_attribute('href')
            shared_id = re.search(
                r'(?<=story_fbid=).*?(?=&)', metadata).group()
            return f'Shared Post: {shared_id}'

        content = None
        if not element.find_elements_by_css_selector(pl['CONTENT']):
            return content
        if element.find_elements_by_css_selector(pl['VIDEO']):
            content = 'Video'
        elif element.find_elements_by_css_selector(pl['STREAM']):
            content = 'Live Stream'
        elif element.find_elements_by_css_selector(pl['PHOTO']):
            content = 'Photo'
        elif element.find_elements_by_css_selector(pl['ALBUM']):
            content = 'Photo Album'
        elif element.find_elements_by_css_selector(pl['LINK']):
            content = 'Link'
        else:
            content = 'Unknown'
        return content

    @staticmethod
    def _parse_text(driver: WebDriver, element: WebElement) -> (str, list):
        mentions = []
        text_area = element.find_elements_by_css_selector(pl['TEXT_AREA'])
        if not text_area:
            return None
        text_area = text_area[0]  # expand to element
        more_link_div = text_area.find_elements_by_css_selector(
            pl['MORE_LINK_DIV'])
        more_link_span = text_area.find_elements_by_css_selector(
            pl['MORE_LINK_SPAN'])
        more_expose = text_area.find_elements_by_css_selector(
            pl['MORE_EXPOSE'])

        # case 1: text is too long and needs to be fully parsed from post's page
        if more_link_div or more_link_span:
            more_link = more_link_div[0] if more_link_div else more_link_span[0]
            post_page_url = more_link.get_attribute('href')
            original_window = driver.current_window_handle
            driver.execute_script("window.open('');")  # open new tab
            driver.switch_to.window(driver.window_handles[1])
            driver.get(post_page_url)
            text_area = driver.find_element_by_css_selector(pl['TEXT_AREA'])
            pgraphs = text_area.find_elements_by_tag_name('p')
            atags = text_area.find_elements_by_css_selector(pl['ATAGS'])
            post_text = [p.get_attribute('innerText') for p in pgraphs]
            mentions = [a.text for a in atags]
            driver.close()  # close tab
            driver.switch_to.window(original_window)

        # case 2: text is too long but can be fully exposed in posts feed
        elif more_expose:
            more_expose[0].click()
            time.sleep(1)
            pgraphs = text_area.find_elements_by_tag_name('p')
            atags = text_area.find_elements_by_css_selector(pl['ATAGS'])
            post_text = [p.get_attribute('innerText') for p in pgraphs]
            mentions = [a.text for a in atags]

        else:
            pgraphs = text_area.find_elements_by_tag_name('p')
            atags = text_area.find_elements_by_css_selector(pl['ATAGS'])
            post_text = [p.get_attribute('innerText') for p in pgraphs]
            mentions = [a.text for a in atags]

        return '\n'.join(post_text), mentions

    @staticmethod
    def _parse_reactions(driver: WebDriver, element: WebElement, post_id: int) -> dict:
        reactions_display = element.find_elements_by_css_selector(pl['REACTIONS'])
        if not reactions_display:
            return None
        reactions = {}
        original_window = driver.current_window_handle
        driver.execute_script("window.open('');") # open new tab
        driver.switch_to.window(driver.window_handles[1])
        driver.get(POST_REACTIONS % post_id)

        rcounters = driver.find_elements_by_css_selector(pl['RCOUNTERS'])
        for counter in rcounters:
            # reaction can be taken from last word of aria-label
            # example: "120 people reacted with Love" => "Love"
            label = counter.get_attribute('aria-label').split()[-1].lower()
            count_str = counter.text.upper()
            if count_str[-1] == 'K':
                count = int(float(count_str[:-1]) * 1000)
            else:
                count = int(count_str)
            reactions[label] = count

        driver.close() # close tab
        driver.switch_to.window(original_window)
        return reactions
