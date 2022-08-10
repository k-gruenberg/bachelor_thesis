from __future__ import annotations
import sys
import os
from os.path import exists
import itertools
from itertools import takewhile, chain
import urllib.parse
import json
from urllib.request import urlopen
import re  # regex
from collections import OrderedDict
import statistics
import math
from typing import List, Tuple, Dict

from WikidataItem import WikidataItem


# Only consider the first N results/ontology mappings for each noun.
# Example for the noun "Credit Cards":
# Q161380, Q111909098, Q51153743, Q87577755, Q108330485, Q106720623, Q83873
#   becomes
# Q161380, Q111909098, Q51153743, Q87577755
#   for N = 4
# (Set this to a very big number to disable this feature.)
HEURISTIC_ONLY_FIRST_N_RESULTS = 4

# When two nouns map to the same ontology entry, assume they are used as
# synonyms in the text and remove all other mappings. 
#
# Example:
# "car"        -> Q1420 (motor car), Q10470 (Carina) 
# "automobile" -> Q1420 (motor car), Q5386 (auto racing)
# => Assume the two nouns are synonyms for Q1420 and remove Q10470 and Q5386.
HEURISTIC_SYNONYMS = True

# Filter out words/nouns that occur frequently on websites or next to data
# and words describing statistical relationships, often occurring next to data,
# see `WORD_BLACKLIST` constant.
HEURISTIC_WORD_BLACKLIST = True

# Filter out ontology mappings to movies, TV series, paintings and bands.
#
# Examples:
# Q1551573 (The Player; 1992 film by Robert Altman)
# Q7316079 (Restaurant; 1998 film by Eric Bross)
# Q27502412 (Restaurant; painting by Olga Rozanova))
# Q7440356 (Seafood; UK band)
HEURISTIC_FILTER_OUT_MOVIES_ETC = True

# Filter out nouns/ontology entries that describe a singular entity and not an
# entity type, i.e. only keep Wikidata entries that have a value for the
# P279 ("subclass of") property.
HEURISTIC_ONLY_KEEP_CLASSES = True

# Use the nltk library to *try* to generate a natural language parse for the
# input text and filter out non-nouns that could not be recognized as non-nouns
# using the naive dictionary approach, e.g. "indicative".
HEURISTIC_FILTER_OUT_NON_NOUNS_USING_NLTK = True

# Filter out ontology mappings that are subclasses of other ontology mappings.
#
# Example:
# Q1420 (motor car) is a subclass of (P279) of Q752870 (motor vehicle)
# When we have both of these in our possible mappings,
# remove the subtype Q1420.
HEURISTIC_USE_SUPERTYPES_ONLY = True

# When set to 1, only the direct supertypes are considered for the
#   HEURISTIC_USE_SUPERTYPES_ONLY heuristic.
# For higher levels, the supertypes of these supertypes are considered as well
#   in a recusive fashion.
# DO NOT SET THIS NUMBER TOO HIGH!!
SUPERTYPES_NUMBER_OF_LEVELS = 1

# Prefer ontology entries with smaller indexes over those with larger indexes.
#
# Example:
# Q11707 (restaurant; single establishment which prepares and serves food,
#                     located in building)
#   vs.
# Q11666766 (restaurant; type of business under Japan's Food Sanitation Law)
HEURISTIC_USE_ONTOLOGY_INDEXES = False

# The word blacklist lists words that occur frequently on websites or next to
# data and words describing statistical relationships, often occurring next to
# data (cf. the fixed keyword sets for SQL aggregation functions used by the
# AggChecker).
WORD_BLACKLIST =\
    ["filter", "information", "home", "count", "number", "total", "sum", "I",\
    "are"]

# Whether to activate debug info prints:
DEBUG = False


def inverse_cantor_pairing_function(z: int) -> Tuple[int, int]:
    # Source:
    # https://en.wikipedia.org/wiki/Pairing_function
    #   #Inverting_the_Cantor_pairing_function
    w = math.floor( (math.sqrt(8*z + 1) - 1) / 2)
    t = (w*w + w)/2
    y = z - t
    x = w - y
    return int(x), int(y)


def noun_match(noun1: str, noun2: str) -> bool:
    """
    Two given nouns match when they are equal or when one of them
    is the plural/singular form of the other one.
    The matching is also case-insensitive.

    This is a basic form of so called "stemming",
    see https://en.wikipedia.org/wiki/Stemming
    """
    noun1 = noun1.lower()
    noun2 = noun2.lower()
    return noun1 == noun2\
        or noun1[-3:] == "ies" and noun2 == noun1[:-3] + "y"\
        or noun2[-3:] == "ies" and noun1 == noun2[:-3] + "y"\
        or noun1[-1:] ==   "s" and noun2 == noun1[:-1]\
        or noun2[-1:] ==   "s" and noun1 == noun2[:-1]\


def filter_nouns_with_heuristics_as_tuple_list(input_text: str, VERBOSE: bool,\
    ALLOW_EQUAL_SCORES: bool) -> List[Tuple[WikidataItem, float]]:  # ToDo !!!!!
    
    if VERBOSE or DEBUG:
        print("")  # separator
    if VERBOSE:
        print("Verbose prints activated.")
    if DEBUG:
        print("Debug prints activated.")

    oxford_dictionary_file_path =\
        os.path.expanduser("~/Oxford_English_Dictionary.txt")
    oxford_dictionary_url =\
        "https://raw.githubusercontent.com/sujithps/Dictionary/master/"\
        "Oxford%20English%20Dictionary.txt"

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
    nouns_with_definition: Dict[str, str] = dict()
    for line in oxford_dictionary_file:
        line = line.strip()  # trim
        if len(line) <= 1:
            # Skip empty lines and lines containing only one character
            #   ("A", "B", "C", ...):
            continue
        if " —n. " in line: # Word has multiple def., one of them is a noun:
            noun = " ".join(list(takewhile(\
                lambda w: w not in ["—n.", "—v.", "—adj."], line.split())))
            # Remove digits from noun (e.g. "Date1"):
            noun = re.sub(r"\d", "", noun)
            # E.g. "Program  (brit. Programme)" => "Program":
            noun = re.sub(r"\(.*\)", "", noun).strip()
            if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
            # The noun definition is everything after the first "—n."
            #   and before the next "—":
            definition = line.split(" —n. ")[1].split("—")[0].strip()
            nouns_with_definition[noun.lower()] =\
                nouns_with_definition.get(noun.lower(), "") + definition
        elif " n. " in line:  # Word has only one definition, which is a noun:
            noun = line.split(" n. ")[0].strip()
            # Remove digits from noun (e.g. "Date2"):
            noun = re.sub(r"\d", "", noun)
            # E.g. "Program  (brit. Programme)" => "Program":
            noun = re.sub(r"\(.*\)", "", noun).strip()
            if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
            definition = line.split(" n. ")[1].strip()
            nouns_with_definition[noun.lower()] =\
                nouns_with_definition.get(noun.lower(), "") + definition
        # skip all words / dictionary entries that are not nouns

    # Now filter all the nouns from the input texts and
    #   print them together with their definition and ontology links:

    # First, generate all noun candidates from the input text
    #   (a noun may consist of multiple words!):
    noun_candidates = []
    words = input_text.split()
    # Remove all non-word chars, otherwise "Restaurants:" will
    #   be a word but not recognized because of the ":" symbol:
    words = [re.sub(r"\W", "", word) for word in words]
    # Longer noun candidates first
    #   (e.g. "credit card" before "credit" and "card"):
    for word_length in range(len(words), 0, -1):
        for index in range(0, len(words) - word_length + 1):
            noun_candidates.append(" ".join(words[index:index+word_length]))
    # print("noun_candidates = " + str(noun_candidates))

    # Second, try to find all these noun candidates in the dictionary:
    successful_matches: List[str] = []
    successful_dict_matches_with_ontology_links:\
        OrderedDict[str, List[WikidataItem]] = OrderedDict([])
    for noun_candidate in noun_candidates:
        if any(map(lambda sm: noun_candidate in sm, successful_matches)):
            # e.g. "credit" but "credit card" has already been matched before
            continue
            # a side effect of this is:
            #   "I" won't be matched anymore either because "credit card"
            #   contains an "i"

        dictionary_match = ""
        if noun_candidate.strip() == "":
            dictionary_match = ""
        elif noun_candidate.lower() in nouns_with_definition:
            dictionary_match = noun_candidate.lower()
        # When the noun candidate is a plural,
        #   look up the singular in the dictionary:
        elif noun_candidate.lower()[-3:] == "ies"\
                and noun_candidate.lower()[:-3] + "y"\
                in nouns_with_definition.keys():
            dictionary_match = noun_candidate.lower()[:-3] + "y"
        elif noun_candidate.lower()[-1:] == "s"\
                and noun_candidate.lower()[:-1]\
                in nouns_with_definition.keys():
            dictionary_match = noun_candidate.lower()[:-1]

        if dictionary_match != "":  # successful match in dictionary:
            successful_matches.append(noun_candidate)
            # e.g. add "credit card" to successful matches

            # Query Wikidata with the noun found to get candidates for
            #   possible matching ontology entries:
            ontology_links: List[WikidataItem] =\
                WikidataItem.get_items_matching_search_string(dictionary_match)
            # Heuristic: keep only the first N results:
            ontology_links = ontology_links[:HEURISTIC_ONLY_FIRST_N_RESULTS] 
            successful_dict_matches_with_ontology_links[dictionary_match] =\
                ontology_links
            if VERBOSE:
                print(dictionary_match + ": "\
                    + str([wikidata_item.entity_id for wikidata_item\
                                                    in ontology_links]))

    nouns = successful_dict_matches_with_ontology_links.keys()

    if VERBOSE:
        print(str(len(nouns)) + " nouns found, with a total of "\
            + str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings: " + str(nouns))

    # Now apply various **heuristics** to reduce the number of results:

    # Remove other mappings for matched nouns that are synonyms:
    # (this should be the first heuristic applied before
    #  any nouns are filtered out)
    if HEURISTIC_SYNONYMS:
        # Consider all pairs of nouns to check if they are synonyms:
        for noun1, noun2 in [(n1, n2) for n1 in nouns for n2 in nouns]:
            if noun1 == noun2:
                continue  # each noun is trivially a synonym for itself
            ontology_links_noun1 =\
                successful_dict_matches_with_ontology_links[noun1]
            ontology_ids_noun1 =\
                [item.entity_id for item in ontology_links_noun1]
            ontology_links_noun2 =\
                successful_dict_matches_with_ontology_links[noun2]
            ontology_ids_noun2 =\
                [item.entity_id for item in ontology_links_noun2]
            ontology_ids_intersection =\
                [_id for _id in ontology_ids_noun1 if _id in ontology_ids_noun2]
            if ontology_ids_intersection != []: # noun1 and noun2 are synonyms:
                if VERBOSE:
                    print("'" + noun1 + "' and '" + noun2\
                        + "' are synonyms; only keeping their intersection: "\
                        + str(ontology_ids_intersection))
                # Remove all other ontology links:
                ontology_links_intersection =\
                    [link for link in ontology_links_noun1\
                     if link.entity_id in ontology_ids_intersection]
                successful_dict_matches_with_ontology_links[noun1] =\
                    ontology_links_intersection
                successful_dict_matches_with_ontology_links[noun2] =\
                    ontology_links_intersection
        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having applied"\
                + " synonym heuristic.")

    # Remove blacklisted words from the successfully matched nouns:
    # (this is done early because it is fast)
    if HEURISTIC_WORD_BLACKLIST:
        successful_dict_matches_with_ontology_links =\
            OrderedDict(list(\
                filter(\
                    lambda pair: pair[0] not in WORD_BLACKLIST,\
                    successful_dict_matches_with_ontology_links.items()\
                )\
            ))
        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having applied"\
                + " word blacklist heuristic.")

    # Remove ontology mappings to movies, TV series, paintings
    #   and bands (musical groups).
    # Use the P31 ("instance of") property for that:
    if HEURISTIC_FILTER_OUT_MOVIES_ETC:
        class_blacklist = ["Q11424",  # "film"
                           "Q5398426",  # "television series"
                           "Q3305213",  # "painting"
                           "Q215380",  # "musical group"
                           "Q7725634"]  # "literary work" 
        successful_dict_matches_with_ontology_links =\
            OrderedDict([(noun,\
            list(\
                filter(\
                    lambda ontology_link:\
                        not any(ontology_link.is_instance_of(_class)\
                            for _class in class_blacklist),\
                    ontology_links\
                )\
            ))\
            for noun, ontology_links\
            in successful_dict_matches_with_ontology_links.items()])
        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having applied"\
                + " movie, TV series, etc. heuristic.")

    # Try to remove subjects (e.g. China) by only keeping classes.
    # Use the P279 ("subclass of", i.e. "next higher class or type")
    #   property for that:
    if HEURISTIC_ONLY_KEEP_CLASSES:
        successful_dict_matches_with_ontology_links =\
            OrderedDict(\
                [(noun, list(\
                    filter(\
                        lambda ontology_link:\
                            ontology_link.get_superclasses(\
                                levels=SUPERTYPES_NUMBER_OF_LEVELS) != [],\
                        ontology_links\
                    )\
                ))\
                for noun, ontology_links in\
                    successful_dict_matches_with_ontology_links.items()\
                ]\
            )
        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having"\
                + " removed everything that is not a subclass of sth.")

    # Filter out ontology mappings that are subclasses of other ontology
    #   mappings.
    # Use the P279 ("subclass of", i.e. "next higher class or type") property
    #   for that:
    if HEURISTIC_USE_SUPERTYPES_ONLY:
        all_ontology_ids: List[str] =\
            [ontology_link.entity_id\
             for noun, ontology_links\
                in successful_dict_matches_with_ontology_links.items()\
             for ontology_link in ontology_links]

        successful_dict_matches_with_ontology_links =\
            OrderedDict([(noun,\
            list(\
                filter(\
                    lambda ontology_link:\
                        not any(superclass in all_ontology_ids\
                        for superclass in ontology_link.get_superclasses(\
                            levels=SUPERTYPES_NUMBER_OF_LEVELS)),\
                    ontology_links\
                )\
            ))\
            for noun, ontology_links\
            in successful_dict_matches_with_ontology_links.items()])

        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having applied"\
                + " supertype-only heuristic.")

    # Use the nltk library to generate a natural language parse tree for the
    # input text and filter out non-nouns that could not be recognized as
    # non-nouns using the naive dictionary approach, example:
    #
    # "The table below lists the vehicles in our fleet.
    #  A team of mechanics reviews them every week."
    #
    # The parse tree includes ('vehicles', 'NNS') and ('reviews', 'VBP'),
    #   i.e. recognizes 'vehicles' as a noun and 'reviews' as a verb.
    # Our heuristic now says that the table could contain 'vehicles'
    #   but it probably does not contain 'reviews'.
    if HEURISTIC_FILTER_OUT_NON_NOUNS_USING_NLTK:
        # Source: https://stackoverflow.com/questions/15388831/
        #           what-are-all-possible-pos-tags-of-nltk
        #         and `nltk.download('tagsets')` command
        NOUN_TAGS = ["NN",  # = noun, common, singular or mass
                     "NNP",  # = noun, proper, singular
                     "NNS",  # = noun, common, plural
                     "NNPS"] # = noun, proper, plural

        # Source: https://stackoverflow.com/questions/42322902/
        #           how-to-get-parse-tree-using-python-nltk
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        from nltk import pos_tag, word_tokenize, RegexpParser
        tagged = pos_tag(word_tokenize(input_text))
        chunker = RegexpParser("""
                        NP: {<DT>?<JJ>*<NN>} #To extract Noun Phrases
                        P: {<IN>}            #To extract Prepositions
                        V: {<V.*>}           #To extract Verbs
                        PP: {<p> <NP>}       #To extract Prepositional Phrases
                        VP: {<V> <NP|PP>*}   #To extract Verb Phrases
                        """)
        parse_tree = chunker.parse(tagged)
        
        # Now we know for each word in the input text whether it is
        #   a noun, verb, determiner, preposition/conjunction, etc.
        # Filter out all "nouns" that never actually occur as a noun in the
        #   text, according to the parse tree:
        non_nouns = []
        for supposed_noun in successful_dict_matches_with_ontology_links.keys():
            all_nltp_tags_for_supposed_noun =\
                list(\
                    map(\
                        lambda leaf: leaf[1],\
                        filter(\
                            lambda leaf: noun_match(leaf[0], supposed_noun),\
                            parse_tree.leaves()\
                        )\
                    )\
                )
            if all_nltp_tags_for_supposed_noun == []:
                # supposed_noun not found in the parse tree so this heuristic
                #   cannot be applied to supposed_noun -> skip it.
                # This occurs for nouns consisting of multiple words, e.g.
                #   "credit card" or "happy hour" when they are separated into
                #   their individual words by the parse tree.
                continue
            if [] == [tag for tag in all_nltp_tags_for_supposed_noun\
                        if tag in NOUN_TAGS]:
                # Supposed_noun isn't actually a noun in the text!
                non_nouns += [supposed_noun]
                if VERBOSE:
                    print(supposed_noun +\
                        " is not actually used a noun in the input text" +\
                        " according to its parse tree but rather as " +\
                        str(all_nltp_tags_for_supposed_noun))

        # After having found all non-nouns, delete them:
        for non_noun in non_nouns:
            del successful_dict_matches_with_ontology_links[non_noun]

        if VERBOSE:
            print(str(sum([len(lst) for lst in\
                    successful_dict_matches_with_ontology_links.values()]))\
                + " ontology mappings left after having applied"\
                + " nouns-only heuristic (parse tree).")


    # At last, after having applied all heuristics, sort the remaining results
    # and print them.
    # Word frequency, original result order and ontology index
    # are used for sorting.

    def word_frequency(word: str) -> int:
        frequency = input_text.lower().count(word.lower())
        if word.lower()[-1] == 'y':
            frequency += input_text.lower().count((word[:-1] + "ies").lower())
            # Example: when word == "country" we also have to add the count of
            #   "countries" on top of the count of "country"
        if DEBUG:
            print("word_frequency(" + word + ") = " + str(frequency))
        return frequency

    if DEBUG:
        print("Nouns before sorting them by word frequency: " +\
            str(successful_dict_matches_with_ontology_links.keys()))

    # First, sort the nouns by how often they appear in the input text:
    successful_dict_matches_with_ontology_links =\
        OrderedDict(\
            sorted(\
                successful_dict_matches_with_ontology_links.items(),\
                key=lambda pair: word_frequency(pair[0]),\
                reverse=True\
            )\
        )

    if DEBUG:
        print("Nouns after sorting them by word frequency: " +\
            str(successful_dict_matches_with_ontology_links.keys()))

    # Second, we have to put all ontology links Q1, Q2, ...
    # into a 1-dimensional list somehow:
    #
    # Noun1:  Q1  Q2  Q3  Q4  Q5
    # Noun2:  Q6  Q7  Q8  Q9 Q10
    # Noun3: Q11 Q12 Q13 Q14 Q15
    # Noun4: Q16 Q17 Q18 Q19 Q20
    # Noun5: Q21 Q22 Q23 Q24 Q25
    #
    # There are multiple ways to do that:
    # (1) in order, left-to-right: [Q1, Q2, Q3, Q4, Q5, Q6, Q7, ...]
    # (2) in order, top-to-bottom: [Q1, Q6, Q11, Q16, Q21, Q2, Q7, ...]
    # (3) using the (inverse) Cantor pairing function:
    #                              [Q1, Q2, Q6, Q3, Q7, Q11, Q4, Q8, ...]
    # * We will not use method (1) since it will put the least-likely search
    #   results too early.
    # * We will use method (2) when all nouns occur with approximately the same
    #   frequency.
    # * We will use method (3) when some nouns are much more common than other
    #   nouns.

    results: List[Tuple[WikidataItem, float]] = []  # output (to be printed)

    frequency_of_most_frequent_word =\
        word_frequency(\
            list(successful_dict_matches_with_ontology_links.keys())[0])
    frequency_of_least_frequent_word =\
        word_frequency(\
            list(successful_dict_matches_with_ontology_links.keys())[-1])
    # If all nouns occur with approximately the same frequency:
    if frequency_of_most_frequent_word - frequency_of_least_frequent_word <= 1:
        # Use method (2):
        if VERBOSE:
            print("Nouns occur with approx. the same frequency: "\
                "list top-to-bottom...")
        # left-to-right:
        for x in range(0, max(\
            [len(ontology_links_for_yth_noun) for ontology_links_for_yth_noun\
            in successful_dict_matches_with_ontology_links.values()]\
            )):
            # top-to-bottom:
            for y in range(0, len(successful_dict_matches_with_ontology_links)):
                ontology_links_for_yth_noun =\
                    list(successful_dict_matches_with_ontology_links.items())\
                        [y][1]
                if x < len(ontology_links_for_yth_noun):
                    ontology_link = ontology_links_for_yth_noun[x]
                    score = todo if ALLOW_EQUAL_SCORES else todo  # ToDo!!!
                    results.append((ontology_link, score))
    else: # Some nouns are much more common than other nouns:
        # Use method (3):
        if VERBOSE:
            print("Some nouns are much more common than others: "\
                "list Cantor-like...")
        total_number_of_ontology_links =\
            sum(map(\
                lambda lst: len(lst),\
                successful_dict_matches_with_ontology_links.values()\
            ))
        i = 0
        while len(results) < total_number_of_ontology_links:
            x, y = inverse_cantor_pairing_function(i)
            if y < len(successful_dict_matches_with_ontology_links.items())\
               and\
               x < len(\
                list(successful_dict_matches_with_ontology_links.items())[y][1]\
               ):
                ontology_link = list(\
                    successful_dict_matches_with_ontology_links.items())\
                    [y][1][x]
                score = word_frequency(todo) + todo / todo\
                    if ALLOW_EQUAL_SCORES else todo  # ToDo!!!
                results.append((ontology_link, score))
            i += 1

    # # Method (1) would have looked like this:
    # results = successful_dict_matches_with_ontology_links.values()
    # # Now we have a list of lists, so flatten it:
    # results = [x for xs in results for x in xs]

    # Remove duplicates (duplicates exist when the text contained synonyms):
    results = list(OrderedDict.fromkeys(results))  # ToDo: new

    # Third, put additional weights on results with a very high ontology index.
    # (E.g. Q11666766 (restaurant;
    #   type of business under Japan's Food Sanitation Law))
    if HEURISTIC_USE_ONTOLOGY_INDEXES:
        ontology_indexes = [int(result.entity_id[1:]) for result in results]
        # (the [1:] strips the "Q" prefix that each Wikidata entry has)
        average_ontology_index = statistics.mean(ontology_indexes)
        ontology_index_standard_deviation = statistics.stdev(ontology_indexes)
        # Put additional weights on ontology entries with whose index is more
        #   than X standard deviations away from the mean/average:
        # ----- this feature/heuristic is not implemented because it does not
        #       appear to make much sense -----

    if VERBOSE: print("")  # separator

    return results


def filter_nouns_with_heuristics_as_list(input_text: str, VERBOSE: bool)\
    -> List[WikidataItem]:
    return [wikidata_item for wikidata_item, score\
        in filter_nouns_with_heuristics_as_tuple_list(\
            input_text=input_text, VERBOSE=VERBOSE, ALLOW_EQUAL_SCORES=False)]

def filter_nouns_with_heuristics_as_dict(input_text: str, VERBOSE: bool,\
    ALLOW_EQUAL_SCORES: bool) -> Dict[WikidataItem, float]:
    return dict(filter_nouns_with_heuristics_as_tuple_list(\
        input_text=input_text,\
        VERBOSE=VERBOSE,\
        ALLOW_EQUAL_SCORES=ALLOW_EQUAL_SCORES))


def main():  # ToDo: argparse  # ToDo: test!!!
    # Whether to activate verbose prints:
    VERBOSE = (len(sys.argv) >= 3 and sys.argv[2] in ["--verbose", "-v"])

    results: List[WikidataItem] =\
        filter_nouns_with_heuristics_as_list(\
            input_text=sys.argv[1], VERBOSE=VERBOSE)

    # At last, print the result:
    for result in results:
        print(result.entity_id + " (" + result.label + "; " +\
            result.description + ")")

if __name__ == "__main__":
    main()
