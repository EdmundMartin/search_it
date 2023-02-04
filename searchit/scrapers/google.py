import asyncio
from typing import List

import bs4

from searchit.scrapers import SearchScraper, ScrapeRequest, SearchResult, ScrapeResponse
from searchit.exceptions import BlockedException


class GoogleScraper(SearchScraper):

    BASE_URL = "https://www.google{}/search?q={}&num={}&hl={}&start={}&filter=0"

    def __init__(self, max_results_per_page: int = 100):
        self.max_results = max_results_per_page

    def _parse_page(self, results: List[SearchResult], res: ScrapeResponse) -> None:
        rank = len(results) + 1
        soup = bs4.BeautifulSoup(res.html, features="html.parser")
        for block in soup.find_all("div", attrs={"class": "g"}):
            link = block.find("a", href=True)
            if link:
                link = link["href"]

            if link.startswith("/") or link.startswith("#"):
                continue

            title = block.find("h3")
            if title:
                title = title.get_text()

            description = block.find("div", {"data-content-feature": "1"})
            if description:
                description = description.get_text()
            results.append(SearchResult(rank, link, title, description))
            rank += 1

    def _check_exceptions(self, res: ScrapeResponse):
        if res.status >= 400:
            raise BlockedException("Google has rate limited this IP address")

    def _paginate(self, term: str, domain: str, language: str, count: int) -> List[str]:
        urls = []
        start = 0
        term = term.replace(" ", "+")
        while start < count:
            num = min(self.max_results, count - start)
            urls.append(self.BASE_URL.format(domain, term, num, language, start))
            start += self.max_results
        return urls

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
