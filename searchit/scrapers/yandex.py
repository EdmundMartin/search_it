import asyncio
from typing import List, Dict

import bs4

from searchit.scrapers.scraper import (
    SearchScraper,
    ScrapeResponse,
    ScrapeRequest,
    SearchResult,
)
from searchit.exceptions import BlockedException, ConfigException


def _clean_yandex_url(url: str) -> str:
    if url.startswith("//"):
        return f"https:{url}"
    return url


def _check_config(max_results: int):
    if max_results > 10:
        raise ConfigException("Yandex max results per page cannot be larger than 10")
    return max_results


class YandexScraper(SearchScraper):

    BASE_URL = "https://yandex{}/search/?text={}&lr={}&p={}"
    DEFAULT_GEO = "10394"

    def __init__(self, max_results_per_page: int = 10):

        self.max_results = _check_config(max_results_per_page)

    def _parse_page(self, results: List[SearchResult], res: ScrapeResponse):
        rank = len(results) + 1
        soup = bs4.BeautifulSoup(res.html, "html.parser")
        for block in soup.find_all("li", attrs={"class": "serp-item"}):
            title_block = block.find("h2", attrs={"class": "organic__title-wrapper"})
            if not title_block:
                continue
            title_text = title_block.get_text()
            url = title_block.find("a", href=True)
            if url:
                url = _clean_yandex_url(url["href"])
            description = block.find("div", attrs={"class": "text-container"})
            if description:
                description = description.get_text()

            results.append(SearchResult(rank, url, title_text, description))
            rank += 1

    def _paginate(self, term: str, domain: str, location: str, count: int) -> List[str]:
        urls = []
        done = 0
        pg = 0
        while done < count:
            term = term.replace(" ", "%20")
            num_doc = min(self.max_results, count - done)
            urls.append(self.BASE_URL.format(domain, term, location, num_doc, pg))
            done += num_doc
            pg += 1
        return urls

    def _check_exceptions(self, res: ScrapeResponse):
        if res.status >= 400:
            raise BlockedException("Yandex has blocked this request")

    @staticmethod
    def user_agent() -> Dict[str, str]:
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-ch-ua": """Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109""",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }

    async def scrape(self, request: ScrapeRequest) -> List[SearchResult]:
        domain = request.domain if request.domain else ".ru"
        location = request.geo if request.geo else self.DEFAULT_GEO
        urls = self._paginate(request.term, domain, location, request.count)
        headers = self.user_agent()
        results = []
        for idx, uri in enumerate(urls):
            response = await self._scrape_one(uri, headers, request.proxy)
            self._check_exceptions(response)
            self._parse_page(results, response)
            if not idx == len(urls) - 1:
                await asyncio.sleep(request.sleep)
        return results


