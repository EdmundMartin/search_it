import asyncio
from typing import List

import bs4

from searchit.scrapers.scraper import (
    SearchScraper,
    ScrapeResponse,
    ScrapeRequest,
    SearchResult,
)
from searchit.exceptions import BlockedException, ConfigException


def _check_config(max_results: int):
    if max_results > 30:
        raise ConfigException('Yandex max results cannot be larger than 30')
    return max_results


class YandexScraper(SearchScraper):

    BASE_URL = "https://yandex{}/search/?text={}&lr={}&numdoc={}&pg={}"
    DEFAULT_GEO = "10394"

    def __init__(self, max_results_per_page: int = 10):

        self.max_results = _check_config(max_results_per_page)

    def _parse_page(self, results: List[SearchResult], res: ScrapeResponse):
        rank = len(results) + 1
        soup = bs4.BeautifulSoup(res.html)
        for block in soup.find_all("ul", attrs={"class": "serp-list"}):
            link = block.find("a", href=True)
            if link:
                link = link["href"]

            if not link.startswith("//"):
                continue
            title = block.find("h2")
            if title:
                title = title.get_text()

            description = soup.find("div", {"class": "organic__content-wrapper"})
            if description:
                description = block.get_text()

            results.append(SearchResult(rank, link, title, description))
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

    async def scrape(self, request: ScrapeRequest) -> List[SearchResult]:
        domain = request.domain if request.domain else ".ru"
        location = request.yandex_geo if request.yandex_geo else self.DEFAULT_GEO
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


if __name__ == '__main__':
    y = YandexScraper()
    request = ScrapeRequest("Екатерина Мартин", 10)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(y.scrape(request))
    print(result)