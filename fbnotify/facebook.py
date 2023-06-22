from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait


@dataclass()
class FacebookResult:
    id: str
    url: str
    text: str
    comments: list[str]


def fetch_head(page: str) -> FacebookResult:
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        webdriver = Chrome(options)
    except WebDriverException as e:
        print(e)

    webdriver.get(f"https://www.facebook.com/{page}")

    web_driver_wait = WebDriverWait(webdriver, 5)
    article = web_driver_wait.until(
        presence_of_element_located(
            (By.CSS_SELECTOR, 'div[role="article"]'),
        )
    )

    links = article.find_elements(By.CSS_SELECTOR, 'a[role="link"]')
    hrefs = map(lambda e: e.get_attribute("href"), links)
    url = [href for href in hrefs if "posts" in href][0]
    if url is None:
        raise Exception()

    post_id = Path(urlparse(url).path).parts[2]

    post = article.find_element(By.CSS_SELECTOR, 'div[data-ad-comet-preview="message"]')
    comments = article.find_elements(By.CSS_SELECTOR, 'span[lang][dir="auto"]')

    return FacebookResult(
        id=post_id,
        url=url,
        text=post.text,
        comments=[comment.text for comment in comments],
    )