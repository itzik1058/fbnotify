from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_all_elements_located,
    presence_of_element_located,
)
from selenium.webdriver.support.wait import WebDriverWait

from fbnotify.utils import logger


@dataclass()
class FacebookPhoto:
    source: str
    description: str


@dataclass()
class FacebookResult:
    page: str
    id: str
    url: str
    text: str
    comments: tuple[str, ...]
    photos: tuple[FacebookPhoto, ...]


class FacebookScraper:
    def __init__(self) -> None:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        try:
            self.webdriver = Chrome(options)
        except WebDriverException as e:
            logger.critical(e)
        self.web_driver_wait = WebDriverWait(self.webdriver, 5)

    def fetch_page_head(self, page: str) -> FacebookResult:
        page_url = f"https://www.facebook.com/{page}"
        self.webdriver.get(page_url)

        article = self.web_driver_wait.until(
            presence_of_element_located(
                (By.CSS_SELECTOR, 'div[role="article"]'),
            )
        )

        link_locator = (By.CSS_SELECTOR, 'a[role="link"]')
        self.web_driver_wait.until(presence_of_all_elements_located(link_locator))
        links = article.find_elements(*link_locator)

        # this fails sometimes
        # maybe try to use WebDriverWait with visibility of subelement
        post_url = [
            link.get_attribute("href")
            for link in links
            if "posts/" in link.get_attribute("href")
        ][0]
        post_id = Path(urlparse(post_url).path).parts[4]

        photos = []
        for link in links:
            if "photo/" not in link.get_attribute("href"):
                continue
            image = link.find_element(By.CSS_SELECTOR, "img")
            description = link.get_attribute("aria-label")
            if description is None:
                description = image.get_attribute("alt")
            photo = FacebookPhoto(
                source=image.get_attribute("src"),
                description=description,
            )
            photos.append(photo)

        try:
            post = article.find_element(
                By.CSS_SELECTOR, 'div[data-ad-comet-preview="message"]'
            )
            text = post.text
            comments = article.find_elements(By.CSS_SELECTOR, 'span[lang][dir="auto"]')
        except NoSuchElementException:
            logger.debug("could not find message element by standard means")
            text = article.text
            comments = []
        logger.info(f"fetch successful for {post_id} at {page_url}")
        return FacebookResult(
            page=page,
            id=post_id,
            url=post_url,
            text=text,
            comments=tuple(comment.text for comment in comments),
            photos=tuple(photos),
        )
