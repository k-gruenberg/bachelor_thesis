# This program takes a list of entries of an identifying column of some table
#   as input and returns an ordered list of class candidates from Wikidata.
# The passed values have to be textual, i.e. strings.
#
# Example inputs:
# * "chevrolet chevelle malibu" "buick skylark 320" "plymouth satellite"
#   => (1) Q3231690 (automobile model)
# * "chevrolet chevelle malibu" "buick skylark 320" "plymouth satellite"...
#   => (20) Q3231690 (automobile model)
#      (2) Q4167410 (Wikimedia disambiguation page)
#      (1) Q1361017 (Ford Torino)
#      (1) Q1137594 (coupé)
# * "malibu" "satellite" "rebel" "challenger" "monte carlo" "corona" "hornet" "firebird"
#   => (4) Q134556 (single)
#      (4) Q16521 (taxon)
#      (3) Q101352 (family name)
#      (3) Q11424 (film)
#      (2) Q1093829 (city of the United States)
#      (2) Q482994 (album)
#      (2) Q5 (human)
#      (2) Q55116 (quarter of Monaco)
#      (2) Q15056993 (aircraft family)
#      (1) Q178780 (liqueur)
#      ...
# * "Mound Station" "Mount Sterling" "Ripley" "Versailles"
#   => (8) Q1093829 (city of the United States)
#      (3) Q62049 (county seat)
#      (2) Q532 (village)
#      (2) Q751708 (village in the United States)
#      (2) Q1115575 (civil parish)
#      (1) Q15221242 (village of Wisconsin)
#      ...
# * "The Stroke" "LONELY IS THE NIGHT" "Everybody Wants You" "My Kinda Lover"
#   => (5) Q134556 (single)
#      (4) Q7366 (song)
#      (2) Q105543609 (musical work/composition)
#      (1) Q215380 (musical group)
#      ...
# * "The Stroke" "LONELY IS THE NIGHT" "Everybody Wants You" "My Kinda Lover"...
#   => (11) Q134556 (single)
#      (8) Q482994 (album)
#      (7) Q7366 (song)
#      (6) Q105543609 (musical work/composition)
#      (3) Q13442814 (scholarly article)
#      (2) Q4167410 (Wikimedia disambiguation page)
#      (2) Q5398426 (television series)
#      (1) Q215380 (musical group)
#      ...
#
# The idea for this approach comes from
#   "Towards Disambiguating Web Tables"
#   by Zwicklbauer, Einsiedler, Granitzer, and Seifert (University of Passau);
#   see Chapter 3 "Approach".
# The difference is that we use Wikidata instead of DBpedia as the ontology.
#
# (ToDo: possibly also consider supertypes!)

from __future__ import annotations
import sys
from collections import defaultdict
from typing import List, Dict

import urllib.parse
import json
from urllib.request import urlopen

DEBUG = False

class WikidataItem:
    API_URL_SEARCH_ENTITIES = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search="
    API_URL_GET_ENTITIES = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbgetentities&format=json&languages=en&ids="\

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

        if self.properties == {}:  # Properties have not been fetched from Wikidata yet:
            api_url = WikidataItem.API_URL_GET_ENTITIES\
                + urllib.parse.quote_plus(self.entity_id)
            json_result = urlopen(api_url).read().decode('utf-8')
            if DEBUG: print("Fetched properties: " + api_url)
            parsed_json = json.loads(json_result)
            
            # First, (try to) set self.label and self.description:
            try:
                self.label = parsed_json["entities"][self.entity_id]\
                    ["labels"]["en"]["value"]
                self.description = parsed_json["entities"][self.entity_id]\
                    ["descriptions"]["en"]["value"]
            except:
                pass

            parsed_properties = parsed_json["entities"][self.entity_id]["claims"]
            for parsed_property in parsed_properties.keys():
                try:
                    self.properties[parsed_property] =\
                        list(
                            map(
                                lambda value:
                                    value if type(value) is str else value.get("id", ""),
                                map(
                                    lambda list_el:
                                        list_el["mainsnak"]["datavalue"]["value"],
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

    @classmethod
    def get_items_matching_search_string(cls, search_string: str) -> List[WikidataItem]:
        api_url = cls.API_URL_SEARCH_ENTITIES\
            + urllib.parse.quote_plus(search_string)
        json_result = urlopen(api_url).read().decode('utf-8')
        if DEBUG: print("Fetched entities: " + api_url)
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

cell_labels: List[str] = sys.argv[1:]  # input values = cell labels

VERBOSE = True

# "Step 1 - Cell entity annotation:
#  For each cell label l[i] we derive a list of k possible entity candidates
#  E[i] using a search-based disambiguation method [5]. We set k = 10 in our
#  experiments." [Zwicklbauer et al.]

entity_candidates_per_label: Dict[str, List[WikidataItem]] =\
    {cell_label: WikidataItem.get_items_matching_search_string(cell_label)\
     for cell_label in cell_labels}

if VERBOSE:
	print("\n##### Finished Step 1 - Cell entity annotation: #####")
	for cell_label, entity_candidates in entity_candidates_per_label.items():
		print(cell_label + ": " + str([str(ec) for ec in entity_candidates]))

# "Step 2 - Entity-type resolution:
#  For each entity candidate e[i]^k in E[i] a set of types is retrieved by
#  following the rdf:type and dcterms:subject relations yielding the set of
#  types T[i]^k." [Zwicklbauer et al.]

types_per_entity_candidate_per_label: Dict[str, Dict[WikidataItem, List[str]]]\
    = {cell_label: {entity_candidate: entity_candidate.get_property("P31")\
                    for entity_candidate in entity_candidates}\
    for cell_label, entity_candidates in entity_candidates_per_label.items()}
# note: P31 = Wikidata's "instance of" property

if VERBOSE:
    print("\n##### Finished Step 2 - Entity-type resolution: #####")
    for cell_label, types_per_entity_candidate in\
        types_per_entity_candidate_per_label.items():
        for entity_candiate, types in types_per_entity_candidate.items():
        	print(cell_label + ": " + entity_candiate.entity_id + ": "\
        		+ str(types))


# "Step 3 - Type aggregation:
#  The types assigned to the table header are the t types that occur most
#  frequently in the set of all types of all cells Union[i] Union[k] T[i]^k.
#  We set t = 1 in our experiments, e.g. only use the most frequent type as
#  result." [Zwicklbauer et al.]

set_of_all_types_of_all_cells_with_frequency: Dict[str, int] =\
    defaultdict(lambda: 0)

for cell_label, types_per_entity_candidate in\
    types_per_entity_candidate_per_label.items():
    for entity_candidate, types in types_per_entity_candidate.items():
        if types is not None:
            for _type in types:
                set_of_all_types_of_all_cells_with_frequency[_type] += 1

if VERBOSE:
    print("\n##### Finished Step 3 - Type aggregation: #####")

for _type, frequency in\
    sorted(set_of_all_types_of_all_cells_with_frequency.items(),\
        key=lambda pair: pair[1], reverse=True):
    print("(" + str(frequency) + ") " + _type + " (" + WikidataItem(_type).get_label() + ")")
