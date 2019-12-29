import asyncio
from typing import List

import bs4

from searchit.scrapers import SearchScraper, ScrapeRequest, SearchResult, ScrapeResponse
from searchit.exceptions import BlockedException, ConfigException


def _check_config(max_results: int):
    if max_results > 30:
        raise ConfigException('Bing max results per page cannot be larger than 30')
    return max_results


class BingScraper(SearchScraper):

    BASE_URL = 'https://www.bing.com/search?q={}&first={}&count={}'

    def __init__(self, max_results_per_page: int = 10):
        self.max_results = _check_config(max_results_per_page)

    def paginate(self, term: str, domain: str, language: str, count: int):
        urls: List[str] = []
        first = 1
        num = 0
        while num < count:
            urls.append(self.BASE_URL.format(term, first, self.max_results))
            num += self.max_results
        return urls
