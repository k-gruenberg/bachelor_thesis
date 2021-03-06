"""
Unlike attr_extension_to_ontology_class.py
which directly retrieves Wikidata ontology entry candidates for every table
cell using "https://www.wikidata.org/w/api.php?action=wbsearchentities";

attr_extension_to_ontology_class_web_search.py performs a web search
for every table cell and uses the text snippets returned by the
web search engine.
"""

from __future__ import annotations
from typing import List, Dict, Set

from enum import Enum

import urllib.parse
import json
from urllib.request import urlopen

import base64
import os
from os.path import exists

import time
import sys

from collections import defaultdict
import re  # regex
from itertools import takewhile

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

        # The free version of the Bing web search API is limited to
        #   3 queries per second:
        time.sleep(0.34)

        # Code below adapted from https://github.com/Azure-Samples/
        #   cognitive-services-REST-api-samples/blob/master/python/Search/
        #   BingWebSearchv7.py:

        # Add your Bing Search V7 subscription key and endpoint to your
        #   environment variables.
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
    try:
        result_list: List[str] = []
        for search_result in json_response["webPages"]["value"]:
            result_list.append(search_result["snippet"])
        return result_list
    except KeyError:
        print("Bing search for '" + search_string + "' yielded no results!")
        return []

nouns_with_definition: Dict[str, str] = {}

def is_noun(word: str) -> bool:  # ToDo: shorten lines!!!!!
    # Code below is adapted from filter_nouns_with_heuristics.py:

    if nouns_with_definition == {}:
        oxford_dictionary_file_path = os.path.expanduser("~/Oxford_English_Dictionary.txt")
        oxford_dictionary_url =\
            "https://raw.githubusercontent.com/sujithps/Dictionary/master/Oxford%20English%20Dictionary.txt"

        # Download the Oxford English Dictionary to a file (if not already) and open that file:
        if not exists(oxford_dictionary_file_path):
            print("Downloading Oxford English Dictionary to " + oxford_dictionary_file_path + "...")
            os.system("wget " + oxford_dictionary_url + " -O " + oxford_dictionary_file_path)
            print("Download complete.")
        oxford_dictionary_file = open(oxford_dictionary_file_path)

        # Filter out only the nouns (and their definitions) from the dictionary file:
        for line in oxford_dictionary_file:
            line = line.strip()  # trim
            if len(line) <= 1:
                continue  # skip empty lines and lines containing only one character ("A", "B", "C", ...)
            if " ???n. " in line:  # word has multiple definitions, one of them is a noun:
                noun = " ".join(list(takewhile(lambda w: w not in ["???n.", "???v.", "???adj."], line.split())))
                noun = re.sub(r"\d", "", noun)  # remove digits from noun (e.g. "Date1")
                noun = re.sub(r"\(.*\)", "", noun).strip()  # e.g. "Program  (brit. Programme)"=>"Program"
                if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
                # the noun definition is everything after the first "???n." and before the next "???":
                definition = line.split(" ???n. ")[1].split("???")[0].strip()
                nouns_with_definition[noun.lower()] =\
                    nouns_with_definition.get(noun.lower(), "") + definition
            elif " n. " in line:  # word has only one definition, which is a noun:
                noun = line.split(" n. ")[0].strip()
                noun = re.sub(r"\d", "", noun)  # remove digits from noun (e.g. "Date2")
                noun = re.sub(r"\(.*\)", "", noun).strip()  # e.g. "Program  (brit. Programme)"=>"Program"
                if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
                definition = line.split(" n. ")[1].strip()
                nouns_with_definition[noun.lower()] =\
                    nouns_with_definition.get(noun.lower(), "") + definition
            # skip all words / dictionary entries that are not nouns
    
    if word.strip() == "":
        return False   # ToDo: also fix in filter_nouns_with_heuristics.py !!!!!
    elif word.lower() in nouns_with_definition:  # ToDo: remove .keys() in filter_nouns_with_heuristics.py !!!!!
        return True
    # when the noun candidate is a plural, look up the singular in the dictionary:
    elif word.lower()[-3:] == "ies" and word.lower()[:-3] + "y"\
            in nouns_with_definition:
        return True
    elif word.lower()[-1:] == "s" and word.lower()[:-1]\
            in nouns_with_definition:  # ToDo: also fix [-1:] in filter_nouns_with_heuristics.py !!!!!
        return True
    else:
        return False


# cf. filter_nouns_with_heuristics.py:  # ToDo: correct there & test again !!!!
def noun_match(noun1: str, noun2: str) -> bool:
    noun1 = noun1.lower()
    noun2 = noun2.lower()
    return noun1 == noun2\
        or noun1[-3:] == "ies" and noun2 == noun1[:-3] + "y"\
        or noun2[-3:] == "ies" and noun1 == noun2[:-3] + "y"\
        or noun1[-1]  ==   "s" and noun2 == noun1[:-1]\
        or noun2[-1]  ==   "s" and noun1 == noun2[:-1]\

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

    # Instead of using a text classifier on the snippets as Quercini & Reynaud
    #   do in their paper "Entity Discovery and Annotation in Tables",
    #   we (...ToDo...)

    # Each noun mapped to the number of snippets it occurs in:  # ToDo: deal with plurals ("car", "cars")
    nouns_to_snippet_count: Dict[str, int] = defaultdict(int)
    for cell_label in cell_labels:
        for snippet in web_search_snippets[cell_label]:
            nouns_in_snippet: Set[str] = set(\
                filter(lambda word: is_noun(word),\
                    map(lambda word: re.sub(r"\W", "", word).lower(),\
                        snippet.split()\
                    )\
                )\
            )
            for noun in nouns_in_snippet:
                nouns_to_snippet_count[noun] += 1

    # Return the nouns ordered by the number of snippets they occur in:
    for noun, count in sorted(nouns_to_snippet_count.items(),\
        key=lambda tuple: tuple[1], reverse=True):
        print("(" + str(count) + ") " + noun)

    # ToDo: Now map these nouns to ontology entries as in approach #1.
    #       This should also get rid of nouns that don't describe types again.
    # ToDo: maybe also get rid of nouns occurring in the parameter strings


if __name__ == "__main__":
    main()

# ToDo: include results in paper !!!!!
