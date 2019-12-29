import asyncio
from typing import List

import bs4

from searchit.scrapers.scraper import SearchScraper, ScrapeResponse, ScrapeRequest, SearchResult
from searchit.exceptions import BlockedException


class YandexScraper(SearchScraper):

    BASE_URL = 'https://yandex{}/search/?text={}&lr={}&numdoc={}&pg={}'
    DEFAULT_GEO = '10394'
    MAX_RESULTS = 10  # technically 30, but Yandex views this highly suspiciously

    def parse_page(self, results: List[SearchResult], res: ScrapeResponse):
        rank = len(results) + 1
        soup = bs4.BeautifulSoup(res.html)
        for block in soup.find_all('ul', attrs={'class': 'serp-list'}):
            link = block.find('a', href=True)
            if link:
                link = link['href']

            if not link.startswith('//'):
                continue
            title = block.find('h2')
            if title:
                title = title.get_text()

            description = soup.find('div', {'class': 'organic__content-wrapper'})
            if description:
                description = block.get_text()

            results.append(SearchResult(rank, link, title, description))
            rank += 1

    def paginate(self, term: str, domain: str, location: str, count: int) -> List[str]:
        urls = []
        done = 0
        pg = 0
        while done < count:
            term = term.replace(' ', '%20')
            print(term)
            num_doc = min(self.MAX_RESULTS, count - done)
            urls.append(self.BASE_URL.format(domain, term, location, num_doc, pg))
            done += num_doc
            pg += 1
        return urls

    def check_exceptions(self, res: ScrapeResponse):
        if res.status >= 400:
            raise BlockedException("Yandex has blocked this request")

    async def scrape(self, request: ScrapeRequest):
        domain = req.domain if req.domain else '.ru'
        location = req.yandex_geo if req.yandex_geo else self.DEFAULT_GEO
        urls = self.paginate(req.term, domain, location, req.count)
        headers = self.user_agent()
        results = []
        for idx, uri in enumerate(urls):
            response = await self._scrape_one(uri, headers, req.proxy)
            self.check_exceptions(response)
            self.parse_page(results, response)
            print(results)
            if not idx == len(urls) - 1:
                await asyncio.sleep(req.sleep)
        return results

