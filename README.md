# searchit
Searchit is a library for async scraping of search engines. The library supports multiple search engines 
(currently Google, Yandex, Qwant and Bing) with support for other search engines to come.

# Install
```
pip install searchit
```
Can be installed using pip, by running the above command.

# Using Searchit
```python
import asyncio

from searchit import GoogleScraper, YandexScraper, BingScraper
from searchit import ScrapeRequest

request = ScrapeRequest("watch movies online", 30)
google = GoogleScraper(max_results_per_page=10) # max_results = Number of results per page
yandex = YandexScraper(max_results_per_page=10)

loop = asyncio.get_event_loop()

results = loop.run_until_complete(google.scrape(request))
results = loop.run_until_complete(yandex.scrape(request))
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
geo - Optional[str] - Geo location to conduct search from Yandex, and Qwant
```

## Roadmap
* Add additional search engines
* Tests
* Blocking non-async scrape method
* Add support for page rendering (Selenium and Puppeteer)