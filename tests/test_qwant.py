import json

import pytest

from searchit.scrapers.qwant import QwantScraper
from searchit.scrapers.scraper import ScrapeResponse


@pytest.yield_fixture(scope="function")
def qwant_json_response():
    with open('./files/qwant.json', 'r') as outfile:
        res_obj = json.load(outfile)
    yield ScrapeResponse("", 200, json=res_obj)


def test_qwant_paginate():
    q = QwantScraper()
    result = q._paginate("watch movies", "", "en_GB", 100)
    assert len(result) == 10


def test_qwant_parse(qwant_json_response):
    q = QwantScraper()
    results = []
    q._parse_json(results, qwant_json_response)
    assert len(results) == 10
