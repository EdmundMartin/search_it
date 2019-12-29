# searchit
Searchit is a library for async scraping of search engines. The library supports multiple search engines 
(currently Google, Yandex, and Bing) with support for other search engines to come.

# Using Searchit
```
from searchit import GoogleScraper, YandexScraper, BingScraper
from searchit import ScrapeRequest

request = ScrapeRequest("watch movies online", 30)
google = GoogleScraper(max_results=10) # max_results = Number of results per page
yandex = YandexScraper(max_results=10)

results = await google.scrape(request)
results = await yandex.scrape(request)
```
To use Searchit users first create a ScrapeRequest object, with term and number of results as required fields. 
This object can then be passed to multiple different search engines and scraped asynchronously.

## Scrape Request - Object
```
term - Required str - the term to be searched for
count - Required int - the total number of results
domain - Optional[str] - the domain to search i.e. .com or .com
sleep - Optional[int] - time to wait betweeen paginating pages - important to prevent getting blocked
proxy - Optional[str] - proxy to be used to make request - default none
language - Optional[str] - language to conduct search in (only Google atm)
yandex_geo - Optional[str] - Yandex location code to conduct search from - default code for London
```

## Roadmap
* Resolve issues with Yandex
* Add additional search engines
* Tests
* Blocking non-async scrape method
* Add support for page rendering (Selenium and Puppeteer)