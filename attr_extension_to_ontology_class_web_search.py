"""
Unlike attr_extension_to_ontology_class.py
which directly retrieves Wikidata ontology entry candidates for every table
cell using "https://www.wikidata.org/w/api.php?action=wbsearchentities";

attr_extension_to_ontology_class_web_search.py performs a web search
for every table cell and uses the text snippets returned by the
web search engine.
"""

from __future__ import annotations
from typing import List, Dict

from enum import Enum

import urllib.parse
import json
from urllib.request import urlopen

import base64
import os

import time

# See https://github.com/Azure-Samples/cognitive-services-REST-api-samples/
#   blob/master/python/Search/BingWebSearchv7.py:
from pprint import pprint
import requests

class SearchEngine(Enum):
    """
    YaCy (pronounced "ya see") is a P2P search engine:
        https://en.wikipedia.org/wiki/YaCy
        https://yacy.net/
     
    Download:
        https://yacy.net/download_installation/
    
    API:
        https://wiki.yacy.net/index.php/Dev:API
        https://wiki.yacy.net/index.php/Dev:APIyacysearch
    
    API Example:
        http://localhost:8090/yacysearch.json?query=plymouth%20satellite
    """
    YACY = 1

    """
    https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

    https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/
        quickstarts/rest/python

    https://portal.azure.com/#view/Microsoft_Bing_Api/

    Official Python example code:
        https://github.com/Azure-Samples/cognitive-services-REST-api-samples/
            blob/master/python/Search/BingWebSearchv7.py

    Free F1
      -> Limit = 3 per second, 1k per month
    """
    BING = 2

    """
    https://serpapi.com/

    Free Plan = 100 searches / month (No Commercial Use)
    """
    GOOGLE_VIA_SERPAPI = 3

API_URL_YACY = "http://localhost:8090/yacysearch.json?query="

def yacy_search_results_descriptions(search_string: str) -> List[str]:
    result: List[str] = []

    api_url = API_URL_YACY + urllib.parse.quote_plus(search_string)
    json_result = urlopen(api_url).read().decode('utf-8')
    parsed_json = json.loads(json_result)

    for yacy_search_result in parsed_json["channels"][0]["items"]:
        #print(yacy_search_result)
        search_result_description = yacy_search_result["description"]
        if search_result_description != "":
            result.append(search_result_description)

    return result

BING_CACHE_PATH = os.path.expanduser(b'~/bing_cache')

def bing_search_results_snippets(search_string: str) -> List[str]:
    # `search_string`, encoded with Base64:
    base64_encoded_search_string =\
        base64.b64encode(search_string.encode(), altchars=b'-_')

    # The parsed JSON response, either from cache or newly retrieved:
    json_response = None

    # Create "~/bing_cache" folder is it does not exist already.
    # If it exists, check whether it really is a directory, as expected:
    if not os.path.exists(BING_CACHE_PATH):
        os.mkdir(BING_CACHE_PATH)
    elif not os.path.isdir(BING_CACHE_PATH):
        print("Fatal error: " + str(BING_CACHE_PATH) + " is not a directory!")
        exit()

    # If we already have the Bing search result for `search_string` cached,
    #   it will be under the following path:
    cached_json_file =\
        os.path.join(BING_CACHE_PATH, base64_encoded_search_string + b'.json')

    if not os.path.exists(cached_json_file):
        # We don't have the results for `search_string` cached yet:

        if 'BING_SEARCH_V7_SUBSCRIPTION_KEY' not in os.environ:
            print("Fatal error: Please set the " +\
                  "BING_SEARCH_V7_SUBSCRIPTION_KEY " +\
                  "environment variable to your Microsoft Bing API Key! " +\
                  "You can find it on portal.azure.com")
            exit()
        elif 'BING_SEARCH_V7_ENDPOINT' not in os.environ:
            print("Fatal error: Please set the " +\
                  "BING_SEARCH_V7_ENDPOINT " +\
                  "environment variable to your Microsoft Bing API Endpoint!" +\
                  "You can find it on portal.azure.com")
            exit()

        # Code below adapted from https://github.com/Azure-Samples/
        #   cognitive-services-REST-api-samples/blob/master/python/Search/
        #   BingWebSearchv7.py:

        # Add your Bing Search V7 subscription key and endpoint to your environment
        #   variables.
        subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
        endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'].rstrip("/") +\
            "/v7.0/search"
            # ...the latter part according to
            # https://docs.microsoft.com/en-us/answers/questions/173628/
            # bing-search-api-returns-the-34resource-not-found34.html
            #
            # https://github.com/Azure-Samples/
            # cognitive-services-REST-api-samples/blob/master/python/Search/
            # BingWebSearchv7.py
            # originally said
            # "/bing/v7.0/search"
            # but that results in a 404 error...
            #
            # Also refer to this issue:
            # https://github.com/Azure-Samples/
            # cognitive-services-REST-api-samples/issues/139

        # Query term(s) to search for. 
        query = search_string

        # Construct a request
        mkt = 'en-US'
        params = { 'q': query, 'mkt': mkt }
        headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

        # Call the API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            #print("\nHeaders:\n")
            #print(response.headers)

            #print("\nJSON Response:\n")
            #pprint(response.json())

            f = open(cached_json_file, "x")
            f.write(response.text)  # https://requests.readthedocs.io/en/latest/
            f.close()
        except Exception as ex:
            raise ex

    # The `cached_json_file` now definitely exists, either it
    #   existed already or it has now been created after querying Bing:
    f = open(cached_json_file, "r")  # open ~/bing_cache/[...].json
    json_response = json.loads(f.read())  # read and parse json file
    f.close()

    # pprint(json_response)

    # Parse `json_response` into List:
    result_list: List[str] = []
    for search_result in json_response["webPages"]["value"]:
        result_list.append(search_result["snippet"])
    return result_list

SEARCH_ENGINE_TO_USE: SearchEngine = SearchEngine.BING

def main():
    # Input values = cell labels, cf. attr_extension_to_ontology_class.py:
    cell_labels: List[str] = sys.argv[1:]

    # Perform a web search for each of these cell labels and store
    #   the result snippets in a list: 
    web_search_snippets: Dict[str, List[str]] = {}
    for cell_label in cell_labels:
        if SEARCH_ENGINE_TO_USE == SearchEngine.YACY:
            web_search_snippets[cell_label] =\
                yacy_search_results_descriptions(cell_label)
        elif SEARCH_ENGINE_TO_USE == SearchEngine.BING:
            web_search_snippets[cell_label] =\
                bing_search_results_snippets(cell_label)
        elif SEARCH_ENGINE_TO_USE == SearchEngine.GOOGLE_VIA_SERPAPI:
            print("Google Search via serpapi.com is not implemented!")
            exit()

        # The free version of the Bing web search API is limited to
        #   3 queries per second:
        time.sleep(0.34)

    # Instead of using a text classifier on the snippets as Quercini & Reynaud
    #   do in their paper "Entity Discovery and Annotation in Tables",
    #   we (...ToDo...)

    # (...ToDo...)

if __name__ == "__main__":
    main()
