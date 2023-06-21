import asyncio
from typing import List

import bs4

from searchit.scrapers import SearchScraper, ScrapeRequest, SearchResult, ScrapeResponse
from searchit.exceptions import BlockedException, ConfigException


def _check_config(max_results: int):
    if max_results > 30:
        raise ConfigException("Bing max results per page cannot be larger than 30")
    return max_results


class BingScraper(SearchScraper):

    BASE_URL = "https://www.bing.com/search?q={}&first={}&count={}"

    def __init__(self, max_results_per_page: int = 10):
        self.max_results = _check_config(max_results_per_page)

    def _parse_page(self, results: List[SearchResult], resp: ScrapeResponse) -> None:
        rank = len(results) + 1
        soup = bs4.BeautifulSoup(resp.html, "html.parser")
        for block in soup.find_all("li", attrs={"class": "b_algo"}):
            link = block.find("a", href=True)
            if link:
                link = link["href"]

            if not link:
                continue

            title = block.find("h2")
            if title:
                title = title.get_text()

            description = block.find("div", {"class": "b_caption"})
            if description:
                description = description.find("p")
                if description:
                    description = description.get_text()
            results.append(SearchResult(rank, link, title, description))
            rank += 1

    def _paginate(self, term: str, domain: str, language: str, count: int):
        urls: List[str] = []
        first = 1
        num = 0
        while num < count:
            urls.append(self.BASE_URL.format(term, first, self.max_results))
            num += self.max_results
        return urls

    def _check_exceptions(self, res: ScrapeResponse) -> None:
        if res.status >= 400:
            raise BlockedException("Blocked by Bing")
        return

    async def scrape(self, req: ScrapeRequest) -> List[SearchResult]:
        domain = req.domain if req.domain else ".com"
        language = req.language if req.language else "en"
        urls = self._paginate(req.term, domain, language, req.count)
        headers = self.user_agent()
        results = []
        for idx, uri in enumerate(urls):
            response = await self._scrape_one(uri, headers, req.proxy)
            self._check_exceptions(response)
            self._parse_page(results, response)
            if not idx == len(urls) - 1:
                await asyncio.sleep(req.sleep)
        return results
