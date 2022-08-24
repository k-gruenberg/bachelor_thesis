from __future__ import annotations
from typing import List

import urllib.parse
import json
from urllib.request import urlopen

import itertools
from itertools import takewhile, chain

import base64
import os
from os.path import exists

DEBUG = False

API_URL_SEARCH_ENTITIES = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbsearchentities"\
        "&format=json&language=en&type=item&continue=0&search="
API_URL_GET_ENTITIES = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbgetentities"\
        "&format=json&languages=en&ids="\

WIKIDATA_SEARCH_CACHE_PATH = os.path.expanduser(b'~/wikidata_search_cache')
WIKIDATA_ENTITY_CACHE_PATH = os.path.expanduser(b'~/wikidata_entity_cache')

def get_cached_wikidata_search(search_string: str) -> str:  # returns JSON
    # `search_string`, encoded with Base64:
    base64_encoded_search_string =\
        base64.b64encode(search_string.encode(), altchars=b'-_')

    # Create "~/wikidata_search_cache" folder is it does not exist already.
    # If it exists, check whether it really is a directory, as expected:
    if not os.path.exists(WIKIDATA_SEARCH_CACHE_PATH):
        os.mkdir(WIKIDATA_SEARCH_CACHE_PATH)
    elif not os.path.isdir(WIKIDATA_SEARCH_CACHE_PATH):
        print("Fatal error: " + str(WIKIDATA_SEARCH_CACHE_PATH)\
            + " is not a directory!")
        exit()

    # If we already have the Wikidata search result for `search_string` cached,
    #   it will be under the following path:
    cached_json_file =\
        os.path.join(WIKIDATA_SEARCH_CACHE_PATH,\
            base64_encoded_search_string + b'.json')

    if not os.path.exists(cached_json_file):
        # We don't have the results for `search_string` cached yet:
        api_url = API_URL_SEARCH_ENTITIES\
            + urllib.parse.quote_plus(search_string)
        json_result = urlopen(api_url).read().decode('utf-8')
        if DEBUG: print("Fetched entities: " + api_url)
        f = open(cached_json_file, "x")
        f.write(json_result)
        f.close()
        return json_result
    else:
        f = open(cached_json_file, "r")  # open JSON file
        json_result = f.read()  # read JSON file
        f.close()  # close JSON file
        return json_result  # return content of JSON file

def get_cached_wikidata_entity(entity_id: str) -> str:  # returns JSON
    # Create "~/wikidata_entity_cache" folder is it does not exist already.
    # If it exists, check whether it really is a directory, as expected:
    if not os.path.exists(WIKIDATA_ENTITY_CACHE_PATH):
        os.mkdir(WIKIDATA_ENTITY_CACHE_PATH)
    elif not os.path.isdir(WIKIDATA_ENTITY_CACHE_PATH):
        print("Fatal error: " + str(WIKIDATA_ENTITY_CACHE_PATH)\
            + " is not a directory!")
        exit()

    # If we already have the Wikidata entity result for `entity_id` cached,
    #   it will be under the following path:
    cached_json_file =\
        os.path.join(WIKIDATA_ENTITY_CACHE_PATH,\
            bytes(entity_id, 'utf-8') + b'.json')

    if not os.path.exists(cached_json_file):
        # We don't have the results for `search_string` cached yet:
        api_url = API_URL_GET_ENTITIES + urllib.parse.quote_plus(entity_id)
        json_result = urlopen(api_url).read().decode('utf-8')
        if DEBUG: print("Fetched properties: " + api_url)
        f = open(cached_json_file, "x")
        f.write(json_result)
        f.close()
        return json_result
    else:
        f = open(cached_json_file, "r")  # open JSON file
        json_result = f.read()  # read JSON file
        f.close()  # close JSON file
        return json_result  # return content of JSON file


class WikidataItem:

    def __init__(self, entity_id: str, label="", description=""):
        self.entity_id = entity_id
        self.label = label
        self.description = description
        self.properties = dict()

    def get_property(self, _property: str) -> List[str]:
        """
        Example:
        >>> result = WikidataItem.get_items_matching_search_string("China")
        >>> prc = result[0]
        >>> prc.get_property("P31")  # P31 = "instance of" property
        ['Q3624078', 'Q842112', 'Q859563', 'Q1520223', 'Q6256', 'Q465613',
         'Q118365', 'Q15634554', 'Q849866']
        """

        if self.properties == {}:
            # Properties have not been fetched from Wikidata (or cache) yet:
            json_result = get_cached_wikidata_entity(self.entity_id)
            parsed_json = json.loads(json_result)
            
            # First, (try to) set self.label and self.description:
            try:
                self.label = parsed_json["entities"][self.entity_id]\
                    ["labels"]["en"]["value"]
                self.description = parsed_json["entities"][self.entity_id]\
                    ["descriptions"]["en"]["value"]
            except:
                pass

            parsed_properties =\
                parsed_json["entities"][self.entity_id]["claims"]
            for parsed_property in parsed_properties.keys():
                try:
                    self.properties[parsed_property] =\
                        list(
                            map(
                                lambda value:
                                    value if type(value) is str\
                                        else value.get("id", ""),
                                map(
                                    lambda list_el:
                                        list_el["mainsnak"]["datavalue"]\
                                        ["value"],
                                    parsed_properties[parsed_property]
                                )
                            )
                        )
                except KeyError:
                    if DEBUG:
                        print("Could not parse property '" + parsed_property\
                            + "' of entity '" + self.entity_id + "'")

        #if DEBUG:
        #    print(\
        #        self.entity_id + ".properties.get(" + _property + ", None) = "\
        #        + str(self.properties.get(_property, None))
        #    )
        return self.properties.get(_property, None)

    def get_superclasses(self, levels=1) -> List[str]:
        # https://www.wikidata.org/wiki/Property:P279 ("subclass of")
        if levels == 0:
            return []
        superclasses = self.get_property("P279")
        if superclasses is None:
            return []
        superclasses = list(itertools.chain.from_iterable(\
            map(\
                lambda superclass:\
                    [superclass] +\
                    WikidataItem(superclass).get_superclasses(levels=levels-1),\
                superclasses\
            )\
        ))
        return superclasses

    def is_subclass_of(self, _id: str) -> bool:
        # https://www.wikidata.org/wiki/Property:P279
        return self.get_property("P279") is not None\
            and _id in self.get_property("P279")

    def is_instance_of(self, _id: str) -> bool:
        # https://www.wikidata.org/wiki/Property:P31 ("instance of")
        return self.get_property("P31") is not None\
            and _id in self.get_property("P31")

    def get_label(self) -> str:
        if self.label == "":
            # Calling self.get_property("") should trigger the retrieval of
            #   all the properties, including the label:
            self.get_property("")
        return self.label

    def __str__(self):
    	if self.label != "":
    		return self.entity_id + " (" + self.label + ")"
    	else:
    		return self.entity_id

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, WikidataItem):
            return self.entity_id == other.entity_id
        return False


    @classmethod
    def get_items_matching_search_string(cls, search_string: str)\
        -> List[WikidataItem]:
        json_result = get_cached_wikidata_search(search_string)
        parsed_json = json.loads(json_result)

        # Return id, label and description for each search result:
        return list(
            map(
                lambda list_el:
                    WikidataItem(
                        entity_id=list_el["id"],
                        label=list_el.get("label", ""),
                        description=list_el.get("description", "")
                     ),
                parsed_json["search"]
            )
        )
