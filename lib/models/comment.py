import re
import time
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from lib.config.locators import comment_loc as cl


@dataclass
class Comment:
    """Holds data of scraped Facebook comment."""
    element: InitVar[WebElement]
    pagename: str
    comment_id: int = field(init=False)
    commenter_id: int = field(init=False)
    commenter_name: str = field(init=False)

    def __post_init__(self, element):
        self.comment_id = self._parse_comment_id(element)
        self.commenter_id = self._parse_commenter_id(element)
        self.commenter_name = self._parse_name(element)
        self.text, self.links = self._parse_text(element, self.commenter_name)
        self.content = self._parse_content(element)

    @staticmethod
    def _parse_comment_id(element: WebElement) -> int:
        return int(element.get_attribute('id'))

    @staticmethod
    def _parse_commenter_id(element: WebElement) -> int:
        data = element.find_element_by_css_selector(cl['PICTURE'])
        fbid = data.get_attribute('data-sigil')
        return int(fbid.replace('feed_story_ring', ''))

    @staticmethod
    def _parse_name(element: WebElement) -> str:
        name_str = element.find_element_by_css_selector(cl['NAME']).text
        return re.sub(r'[Tt]op [Ff]an|[Aa]uthor|\n', '', name_str)

    @staticmethod
    def _parse_text(element: WebElement, cname: str) -> str:
        body = element.find_elements_by_css_selector(cl['BODY'])
        if not body:
            return None, None
        text = body[0].text
        # in some cases commenter names gets into the text, remove them
        text = None if text == cname else text
        atags = body[0].find_elements_by_css_selector(cl['LINKS'])
        links = None if not atags else [tag.text for tag in atags]
        # if text is entirely the first link, then there is no text
        text = None if links and links[0] == text else text
        return text, links

    @staticmethod
    def _parse_content(element: WebElement) -> dict:
        # lambda functions for content link encoding
        encode_gif = lambda url: url.replace('%3A', ':').replace('%2F', '/')\
                .replace('%3F', '?').replace('%3D', '=').replace('%26', '&')
        encode_sticker = lambda url: url.replace('\3a ', ':')\
            .replace('\3d ', '=').replace('\26 ', '&')
        encode_image = lambda url: url.replace(r'\/','/')

        # possible locators
        gif = element.find_elements_by_css_selector(cl['GIF'])
        sticker = element.find_elements_by_css_selector(cl['STICKER'])
        image = element.find_elements_by_css_selector(cl['IMAGE'])

        if gif:
            clink = gif[0].find_element_by_tag_name('a').get_attribute('href')
            clink = re.search(r'(?<=u=).*?(?=&)', clink).group()
            return {'type': 'GIF', 'link': encode_gif(clink)}

        if sticker:
            clink = sticker[0].get_attribute('style')
            clink = re.search(r'(?<=url\([\"\']).*?(?=[\"\'])', clink).group()
            return {'type': 'Sticker', 'link': encode_sticker(clink)}

        if image:
            clink = image[0].get_attribute('data-store')
            clabel = image[0].get_attribute('label')
            if clabel:
                clabel = re.findall(r'(?<=text that says [\"\']).*?(?=[\"\'])', clabel)
                clabel = clabel[0] if clabel else None
            clink = re.search(r'(?<={\"imgsrc\":\").*?(?=\"})', clink).group()
            return {'type': 'Image', 'link': encode_image(clink), 'label': clabel}

        return None
