import pytest

from searchit.scrapers.yandex import YandexScraper
from searchit.scrapers.scraper import ScrapeResponse


@pytest.yield_fixture(scope='function')
def yandex_response():
    with open('./files/yandex.html', 'r', errors='ignore') as yandex_html:
        yield ScrapeResponse(yandex_html.read(), 200)


def test_yandex_parsing(yandex_response):
    y = YandexScraper()
    results = []
    y._parse_page(results, yandex_response)
    assert len(results) == 13
