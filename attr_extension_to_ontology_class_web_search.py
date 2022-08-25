"""
Unlike attr_extension_to_ontology_class.py
which directly retrieves Wikidata ontology entry candidates for every table
cell using "https://www.wikidata.org/w/api.php?action=wbsearchentities";

attr_extension_to_ontology_class_web_search.py performs a web search
for every table cell and uses the text snippets returned by the
web search engine.
"""

from __future__ import annotations
from typing import List, Dict, Set, Tuple

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

import argparse

from filter_nouns_with_heuristics import\
    filter_nouns_with_heuristics_as_list,\
    filter_nouns_with_heuristics_as_dict,\
    filter_nouns_with_heuristics_as_tuple_list,\
    noun_match

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
    
    try:
        json_result = urlopen(api_url).read().decode('utf-8')
    except:
        print("Fatal error: YaCy does not seem to be available at " + api_url)
        exit()
    
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

        print(f"Debug: {cached_json_file} not found")

        if 'BING_SEARCH_V7_SUBSCRIPTION_KEY' not in os.environ:
            print("Fatal error: Please set the " +\
                  "BING_SEARCH_V7_SUBSCRIPTION_KEY " +\
                  "environment variable to your Microsoft Bing API Key! " +\
                  "You can find it on portal.azure.com")
            exit()
        elif 'BING_SEARCH_V7_ENDPOINT' not in os.environ:
            print("Fatal error: Please set the " +\
                  "BING_SEARCH_V7_ENDPOINT " +\
                  "environment variable to your Microsoft Bing API Endpoint!"+\
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
            f.write(response.text)  #https://requests.readthedocs.io/en/latest/
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

def is_noun(word: str) -> bool:  # ToDo: maybe avoid code duplication
    # Code below is adapted from filter_nouns_with_heuristics.py:

    if nouns_with_definition == {}:
        oxford_dictionary_file_path =\
            os.path.expanduser("~/Oxford_English_Dictionary.txt")
        oxford_dictionary_url =\
            "https://raw.githubusercontent.com/sujithps/Dictionary/" +\
            "master/Oxford%20English%20Dictionary.txt"

        # Download the Oxford English Dictionary to a file (if not already)
        #   and open that file:
        if not exists(oxford_dictionary_file_path):
            print("Downloading Oxford English Dictionary to " +\
                oxford_dictionary_file_path + "...")
            os.system("wget " + oxford_dictionary_url + " -O " +\
                oxford_dictionary_file_path)
            print("Download complete.")
        oxford_dictionary_file = open(oxford_dictionary_file_path)

        # Filter out only the nouns (and their definitions)
        #   from the dictionary file:
        for line in oxford_dictionary_file:
            line = line.strip()  # trim
            if len(line) <= 1:
                # Skip empty lines and lines containing only
                #   one character ("A", "B", "C", ...):
                continue
            if " —n. " in line:
                # Word has multiple definitions, one of them is a noun:
                noun = " ".join(list(takewhile(\
                    lambda w: w not in ["—n.", "—v.", "—adj."], line.split())))
                # Remove digits from noun (e.g. "Date1"):
                noun = re.sub(r"\d", "", noun)
                # Remove parentheses,
                #   e.g. turn "Program  (brit. Programme)" into "Program":
                noun = re.sub(r"\(.*\)", "", noun).strip()
                if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
                # The noun definition is everything after the first "—n."
                #   and before the next "—":
                definition = line.split(" —n. ")[1].split("—")[0].strip()
                nouns_with_definition[noun.lower()] =\
                    nouns_with_definition.get(noun.lower(), "") + definition
            elif " n. " in line:
                # Word has only one definition, which is a noun:
                noun = line.split(" n. ")[0].strip()
                # Remove digits from noun (e.g. "Date2"):
                noun = re.sub(r"\d", "", noun)
                # Remove parentheses,
                #   e.g. turn "Program  (brit. Programme)" into "Program":
                noun = re.sub(r"\(.*\)", "", noun).strip()
                if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
                definition = line.split(" n. ")[1].strip()
                nouns_with_definition[noun.lower()] =\
                    nouns_with_definition.get(noun.lower(), "") + definition
            # skip all words / dictionary entries that are not nouns
    
    if word.strip() == "":
        return False
    elif word.lower() in nouns_with_definition:
        return True
    # When the noun candidate is a plural,
    #   look up the singular in the dictionary:
    elif word.lower()[-3:] == "ies" and word.lower()[:-3] + "y"\
            in nouns_with_definition:
        return True
    elif word.lower()[-1:] == "s" and word.lower()[:-1]\
            in nouns_with_definition:
        return True
    else:
        return False


def attr_extension_to_ontology_class_web_search(cell_labels: List[str],\
    k: int = 30, search_engine: SearchEngine = SearchEngine.BING)\
    -> List[Tuple[str, int]]:
    """
    This function takes the same `cell_labels` argument as the
    attr_extension_to_ontology_class() function in
    attr_extension_to_ontology_class.py but instead of a
    Dict[WikidataItem, int] (mapping WikidataItem's to scores)
    it returns a
    List[Tuple[str, int]] (mapping nouns to scores; where the nouns already
    capture the semantics of the table, ideally the entity type of the tuples).

    The `k` parameter specifies the maximum number of nouns that shall be
    in the returned dictionary. By default, it is set to 30.
    Set it to -1 to return the complete dictionary - this is not recommended
    though because the total number of nouns might be quite large!

    The default `search_engine` is `BING` and it is recommended to leave it
    that way! The other options would be `YACY` (bad results) and
    `GOOGLE_VIA_SERPAPI` (not implemented).

    Example:

    attr_extension_to_ontology_class_web_search(["Manuel Neuer",
    "Joshua Kimmich", "Kai Havertz", "Marco Reus", "Timo Werner",
    "Serge Gnabry", "Antonio Rüdiger"], k=5)
    ==
    [('club', 20), ('german', 14), ('professional', 12), ('team', 12),
    ('player', 12)]
    """
    
    # Perform a web search for each of these cell labels and store
    #   the result snippets in a list: 
    web_search_snippets: Dict[str, List[str]] = {}
    for cell_label in cell_labels:
        if search_engine == SearchEngine.YACY:
            web_search_snippets[cell_label] =\
                yacy_search_results_descriptions(cell_label)
        elif search_engine == SearchEngine.GOOGLE_VIA_SERPAPI:
            print("Google Search via serpapi.com is not implemented!")
            exit()
        else:  # Default: Use Bing:
            web_search_snippets[cell_label] =\
                bing_search_results_snippets(cell_label)

    # Instead of using a text classifier on the snippets as Quercini & Reynaud
    #   do in their paper "Entity Discovery and Annotation in Tables",
    #   we use the idea from filter_nouns_heuristics.py again and look and the
    #   most common nouns from the snippets.
    # When the user specified the `--list-onto` we also map these nouns to the
    #   Wikidata ontology again.

    # Each noun mapped to the number of snippets it occurs in:
    nouns_to_snippet_count: Dict[str, int] = defaultdict(int)
    for cell_label in cell_labels:
        for snippet in web_search_snippets[cell_label]:
            nouns_in_snippet: Set[str] = set(\
                filter(lambda word: is_noun(word),\
                    map(lambda word: re.sub(r"\W", "", word).lower(),\
                        snippet.split()\
                    )\
                )\
            )  #ToDo: maybe(!) multi-word nouns (has disadvantages, see thesis)
            for noun in nouns_in_snippet:
                nouns_to_snippet_count[noun] += 1

    # Merge singular and plural form of the same noun, e.g. "car" and "cars":
    nouns: List[str] = list(nouns_to_snippet_count.keys())
    for noun1 in nouns:
        for noun2 in nouns:
            if noun1 != noun2 and noun_match(noun1, noun2):
                singular = noun1 if len(noun1) <= len(noun2) else noun2
                plural   = noun2 if len(noun1) <= len(noun2) else noun1
                nouns_to_snippet_count[singular] +=\
                    nouns_to_snippet_count[plural]
                del nouns_to_snippet_count[plural]

    nouns_to_snippet_count_sorted: List[Tuple[str, int]] =\
        sorted(nouns_to_snippet_count.items(),\
            key=lambda tuple: tuple[1], reverse=True)

    # Only consider the K most common nouns:
    if k >= 0:
        nouns_to_snippet_count_sorted = nouns_to_snippet_count_sorted[:k]

    return nouns_to_snippet_count_sorted

    # ToDo: maybe also get rid of nouns occurring in the parameter strings


def attr_extension_to_ontology_class_web_search_concat_nouns(\
    cell_labels: List[str],\
    k: int = 30, search_engine: SearchEngine = SearchEngine.BING) -> str:
    """
    This concatenated string can be used in approach #1
    (filter_nouns_with_heuristics.py)
    which should also get rid of nouns that don't describe types again.
    """

    nouns_to_snippet_count_sorted =\
        attr_extension_to_ontology_class_web_search(\
        cell_labels=cell_labels, k=k, search_engine=search_engine)
    
    concatenated_string: str = ""
    for noun, count in nouns_to_snippet_count_sorted:
        concatenated_string += (noun + " ") * count + "xxxxx "

    return concatenated_string


def attr_extension_to_ontology_class_web_search_list_onto_as_tuple_list(\
    cell_labels: List[str],\
    k: int = 30, search_engine: SearchEngine = SearchEngine.BING,\
    VERBOSE: bool = False) -> List[Tuple[WikidataItem, float]]:
    return filter_nouns_with_heuristics_as_tuple_list(\
        input_text=attr_extension_to_ontology_class_web_search_concat_nouns(\
            cell_labels=cell_labels, k=k, search_engine=search_engine),\
        VERBOSE=VERBOSE)


def attr_extension_to_ontology_class_web_search_list_onto_as_list(\
    cell_labels: List[str],\
    k: int = 30, search_engine: SearchEngine = SearchEngine.BING,\
    VERBOSE: bool = False) -> List[WikidataItem]:
    return filter_nouns_with_heuristics_as_list(\
        input_text=attr_extension_to_ontology_class_web_search_concat_nouns(\
            cell_labels=cell_labels, k=k, search_engine=search_engine),\
        VERBOSE=VERBOSE)


def attr_extension_to_ontology_class_web_search_list_onto_as_dict(\
    cell_labels: List[str],\
    k: int = 30, search_engine: SearchEngine = SearchEngine.BING,\
    VERBOSE: bool = False) -> Dict[WikidataItem, float]:
    return filter_nouns_with_heuristics_as_dict(\
        input_text=attr_extension_to_ontology_class_web_search_concat_nouns(\
            cell_labels=cell_labels, k=k, search_engine=search_engine),\
        VERBOSE=VERBOSE)


def main():
    parser = argparse.ArgumentParser(
        description="""
        This tool takes the extension of an identifying table column as input
        and performs a web search for each of these table cells,
        in order to find out the entity type of the tuples of the table.
        """)

    # Input values = cell labels, cf. attr_extension_to_ontology_class.py:
    parser.add_argument(
        'cell_labels',
        type=str,
        help="""
        The extension of an identifying table column, e.g.
        "chevrolet chevelle malibu" "buick skylark 320"
        "plymouth satellite" ...
        """,
        nargs='*',
        metavar='CELL_LABEL')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--yacy', action='store_true',
        help="Use the YaCy P2P search engine (implemented but bad).")
    group1.add_argument('--bing', action='store_true',
        help="""Use the Bing search engine (default, use this).
        API Key required.""")
    group1.add_argument('--google', action='store_true',
        help="Use the Google search engine (not implemented).")

    parser.add_argument('-k',
        type=int,
        default=30,
        help="""Only consider the k most common nouns.
        Such a limit is necessary because the total number of nouns in all
        search result snippets is generally quite large.
        Default value: 30""",
        metavar='K')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('--list-nouns', action='store_true',
        help="""
        List the top-k most common nouns in descending order (default).
        """)
    group2.add_argument('--concat-nouns', action='store_true',
        help="""
        Concatenate the top-k most common nouns into a single output string,
        separated by ' xxxxxx ' and in between each noun repeated as many
        times as it occurred.
        """)
    group2.add_argument('--list-onto', action='store_true',
        help="""
        Take the output of --concat, give it to
        filter_nouns_with_heuristics.py and output its results, i.e.
        an ordered list of ontology mappings for the top-k most common nouns.
        """)

    args = parser.parse_args()

    search_engine: SearchEngine = SearchEngine.BING  # = default search engine
    if args.yacy:
        search_engine = SearchEngine.YACY
    elif args.google:
        search_engine = SearchEngine.GOOGLE_VIA_SERPAPI

    if args.concat_nouns:
        concatenated_string: str =\
            attr_extension_to_ontology_class_web_search_concat_nouns(\
                cell_labels=args.cell_labels, k=args.k,
                search_engine=search_engine)
        print(concatenated_string)
    elif args.list_onto:
        results: List[WikidataItem] =\
            attr_extension_to_ontology_class_web_search_list_onto_as_list(\
                cell_labels=args.cell_labels, k=args.k,
                search_engine=search_engine)

        # Print the result:
        for result in results:
            print(result.entity_id + " (" + result.label + "; " +\
                result.description + ")")
    else:  # Default: args.list_nouns:
        # Return the nouns ordered by the number of snippets they occur in:

        nouns_to_snippet_count_sorted: List[Tuple[str, int]] =\
        attr_extension_to_ontology_class_web_search(\
            cell_labels=args.cell_labels, k=args.k,
            search_engine=search_engine)

        for noun, count in nouns_to_snippet_count_sorted:
            print("(" + str(count) + ") " + noun)


if __name__ == "__main__":
    main()
