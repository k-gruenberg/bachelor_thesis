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
# * "malibu" "satellite" "rebel" "challenger" "monte carlo" "corona"
#   "hornet" "firebird"
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

from WikidataItem import WikidataItem

DEBUG = False

VERBOSE = (__name__ == "__main__")

def attr_extension_to_ontology_class(cell_labels: List[str])\
    -> Dict[WikidataItem, int]:

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

    # Transform the String names of the Wikidata types
    #   into WikidataItems before returning them:
    set_of_all_types_of_all_cells_with_frequency: Dict[WikidataItem, int] =\
        {WikidataItem(_type): frequency for _type, frequency in\
        set_of_all_types_of_all_cells_with_frequency.items()}

    return set_of_all_types_of_all_cells_with_frequency


def main():  # ToDo
    cell_labels: List[str] = sys.argv[1:]  # input values = cell labels

    set_of_all_types_of_all_cells_with_frequency: Dict[WikidataItem, int] =\
        attr_extension_to_ontology_class(cell_labels)

    for _type, frequency in\
        sorted(set_of_all_types_of_all_cells_with_frequency.items(),\
        key=lambda pair: pair[1], reverse=True):
        print("(" + str(frequency) + ") " + _type.entity_id +\
            " (" + _type.get_label() + ")")

if __name__ == "__main__":
    main()
