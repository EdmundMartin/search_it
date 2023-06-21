import asyncio
from typing import Dict, List, Optional

from aiohttp import ClientSession, ClientError

from searchit.scrapers import SearchScraper, ScrapeRequest, SearchResult, ScrapeResponse
from searchit.exceptions import BlockedException, ConfigException


def _check_config(max_results: int):
    if max_results > 10:
        raise ConfigException("Qwant max results per page cannot be larger than 10")
    return max_results


class QwantScraper(SearchScraper):

    BASE_URL = (
        "https://api.qwant.com/v3/search/web?count={}&offset={}"
        "&q={}&t=web&device=desktop&extensionDisabled=true&safesearch=0&locale={}&uiv=4"
    )

    def __init__(self, max_results_per_page: int = 10):
        self.max_results = _check_config(max_results_per_page)

    async def _scrape_one(
        self, url: str, headers: Dict[str, str], proxy: Optional[str]
    ) -> ScrapeResponse:
        async with ClientSession() as client:
            try:
                async with client.get(
                    url, headers=headers, proxy=proxy, timeout=60
                ) as response:
                    json = await response.json()
                    return ScrapeResponse("", response.status, json=json)
            except ClientError as err:
                raise err

    def _parse_json(self, results: List[SearchResult], resp: ScrapeResponse) -> None:
        data = resp.json['data']['result']['items']["mainline"]
        items: List[Dict] = []
        for listing in data:
            context = listing.get('items')
            if context:
                for c in context:
                    items.append(c)
        for search_result in items:
            title = search_result.get("title")
            url = search_result.get("url")
            if url is None:
                continue
            description = search_result.get("description")
            position = len(results) + 1
            results.append(SearchResult(position, url, title, description))

    def _paginate(self, term: str, _: str, geo: str, count: int):
        urls: List[str] = []
        offset = 0
        term = term.replace(" ", "%20")
        while offset < count:
            urls.append(self.BASE_URL.format(self.max_results, offset, term, geo))
            offset += self.max_results
        return urls

    def _check_exceptions(self, res: ScrapeResponse) -> None:
        if res.json["status"] != "success":
            raise BlockedException("Qwant request was not successful")
        return

    async def scrape(self, req: ScrapeRequest) -> List[SearchResult]:
        geo = req.geo if req.geo else "en_GB"
        urls = self._paginate(req.term, "", geo, req.count)
        headers = self.user_agent()
        results = []
        for idx, uri in enumerate(urls):
            response = await self._scrape_one(uri, headers, req.proxy)
            self._check_exceptions(response)
            self._parse_json(results, response)
            if not idx == len(urls) - 1:
                await asyncio.sleep(req.sleep)
        return results
