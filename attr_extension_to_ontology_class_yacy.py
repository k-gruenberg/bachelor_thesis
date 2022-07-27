# ToDo

# YaCy (pronounced "ya see") is a P2P search engine:
#   https://en.wikipedia.org/wiki/YaCy
#   https://yacy.net/
# 
# Download:
#   https://yacy.net/download_installation/
#
# API:
#   https://wiki.yacy.net/index.php/Dev:API
#   https://wiki.yacy.net/index.php/Dev:APIyacysearch
#
# API Example:
#   http://localhost:8090/yacysearch.json?query=plymouth%20satellite

from typing import List

import urllib.parse
import json
from urllib.request import urlopen

API_URL = "http://localhost:8090/yacysearch.json?query="

def yacy_search_results_descriptions(search_string: str) -> List[str]:
    result: List[str] = []

    api_url = API_URL + urllib.parse.quote_plus(search_string)
    json_result = urlopen(api_url).read().decode('utf-8')
    parsed_json = json.loads(json_result)

    for yacy_search_result in parsed_json["channels"][0]["items"]:
        #print(yacy_search_result)
        search_result_description = yacy_search_result["description"]
        if search_result_description != "":
            result.append(search_result_description)

    return result
