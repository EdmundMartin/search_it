from abc import ABCMeta, abstractmethod
from random import choice
from typing import Dict, List, Optional

from aiohttp import ClientSession, ClientError


_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
]


class ScrapeRequest:
    def __init__(
        self,
        term: str,
        count: int,
        domain: Optional[str] = None,
        sleep: int = 0,
        proxy: Optional[str] = None,
        language: Optional[str] = None,
        geo: Optional[str] = None,
    ):
        self.term = term
        self.count = count
        self.domain = domain
        self.sleep = sleep
        self.proxy = proxy
        self.language = language
        self.geo = geo


class ScrapeResponse:
    def __init__(self, html: str, status: int, json: Optional[Dict] = None):
        self.html = html
        self.json = json
        self.status = status

    def __repr__(self):
        return "<ScrapeResponse: html:{}, status:{}>".format(
            self.html[:10], self.status,
        )


class SearchResult:
    def __init__(
        self, rank: int, url: int, title: str, description: str,
    ):
        self.rank = rank
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return "<SearchResult: Rank:{}, URL: {}>".format(self.rank, self.url)


class SearchScraper(metaclass=ABCMeta):
    @staticmethod
    def user_agent() -> Dict[str, str]:
        return {
            "User-Agent": choice(_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    async def _scrape_one(
        self, url: str, headers: Dict[str, str], proxy: Optional[str]
    ) -> ScrapeResponse:
        async with ClientSession() as client:
            try:
                async with client.get(
                    url, headers=headers, proxy=proxy, timeout=60
                ) as response:
                    html = await response.text()
                    return ScrapeResponse(html, response.status)
            except ClientError as err:
                raise err

    @abstractmethod
    def _check_exceptions(self, res: ScrapeResponse) -> None:
        pass

    @abstractmethod
    def _paginate(self, term: str, domain: str, language: str, count: int) -> List[str]:
        pass

    @abstractmethod
    async def scrape(self, request: ScrapeRequest):
        pass
