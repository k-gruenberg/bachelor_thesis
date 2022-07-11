import sys
import os  # ToDo: "Program (brit. Programme)" !!!! (also filter_nouns.py !!!!)
from os.path import exists
from itertools import takewhile
import urllib.parse
import json
from urllib.request import urlopen
import re  # regex
from collections import OrderedDict
import statistics
import math


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

# Filter out nouns/ontology entries that describe a singular entity and not an entity type,
# i.e. only keep Wikidata entries that have a value for the P279 ("subclass of") property.
HEURISTIC_ONLY_KEEP_CLASSES = True

# Use the nltk library to *try* to generate a natural language parse for the input
# text and filter out non-nouns that could not be recognized as non-nouns using
# the naive dictionary approach, e.g. "indicative".
HEURISTIC_FILTER_OUT_NON_NOUNS_USING_NLTK = True

# Filter out ontology mappings that are subclasses of other ontology mappings.
#
# Example:
# Q1420 (motor car) is a subclass of (P279) of Q752870 (motor vehicle)
# When we have both of these in our possible mappings, remove the subtype Q1420.
HEURISTIC_USE_SUPERTYPES_ONLY = True

# Prefer ontology entries with smaller indexes over those with larger indexes.
#
# Example:
# Q11707 (restaurant; single establishment which prepares and serves food, located in building)
#   vs.
# Q11666766 (restaurant; type of business under Japan's Food Sanitation Law)
HEURISTIC_USE_ONTOLOGY_INDEXES = True

# The word blacklist lists words that occur frequently on websites or next to data
# and words describing statistical relationships, often occurring next to data
# (cf. the fixed keyword sets for SQL aggregation functions used by the AggChecker).
WORD_BLACKLIST =\
    ["filter", "information", "home", "count", "number", "total", "sum", "I", "are"]


def get_wikidata_entry_candidates(search_string):
    api_url = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search="\
        + urllib.parse.quote_plus(search_string)
    json_result = urlopen(api_url).read().decode('utf-8')
    parsed_json = json.loads(json_result)

    # Return a tuple of id, label and description for each search result:
    return list(
        map(
            lambda list_el:
                (list_el["id"],
                 list_el.get("label", ""),
                 list_el.get("description", "")),
            parsed_json["search"]
        )
    )

# Example: get_wikidata_properties(entity_id = "Q42") =
#          {'P31': 'Q5', 'P21': 'Q6581097', 'P106': 'Q214917', ...} # ToDo: multiple values => lists!!!
# Note that only the first (0th) value is returned when a property has multiple values!
def get_wikidata_properties(entity_id):
    api_url = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbgetentities&format=json&languages=en&ids="\
        + urllib.parse.quote_plus(entity_id)
    json_result = urlopen(api_url).read().decode('utf-8')
    parsed_json = json.loads(json_result)
    #
    properties = parsed_json["entities"][entity_id]["claims"]
    property_value_pairs =\
        {_property : properties[_property][0]["mainsnak"]["datavalue"]["value"]\
        for _property in properties.keys()\
        if "mainsnak" in properties[_property][0]\
        and "datavalue" in properties[_property][0]["mainsnak"]\
        and "value" in properties[_property][0]["mainsnak"]["datavalue"]}
    # Sometimes the value is a string directly and sometimes one has to get the id attribute:
    property_value_pairs =\
        {_property: value if type(value) is str else value.get("id", "") \
        for _property, value in property_value_pairs.items()}
    return property_value_pairs

def inverse_cantor_pairing_function(z):
    # Source:
    # https://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    w = math.floor( (math.sqrt(8*z + 1) - 1) / 2)
    t = (w*w + w)/2
    y = z - t
    x = w - y
    return int(x), int(y)

input_text = sys.argv[1]  # the text to filter for nouns
DEBUG = (len(sys.argv) >= 3 and sys.argv[2] == "--debug")  # whether to activate debug prints
if DEBUG:
    print("")  # separator
    print("Debug prints activated.")

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
nouns_with_definition = dict()
for line in oxford_dictionary_file:
    line = line.strip()  # trim
    if len(line) <= 1:
        continue  # skip empty lines and lines containing only one character ("A", "B", "C", ...)
    if " —n. " in line:  # word has multiple definitions, one of them is a noun:
        noun = " ".join(list(takewhile(lambda w: w not in ["—n.", "—v.", "—adj."], line.split())))
        noun = re.sub(r"\d", "", noun)  # remove digits from noun (e.g. "Date1")
        if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
        # the noun definition is everything after the first "—n." and before the next "—":
        definition = line.split(" —n. ")[1].split("—")[0].strip()
        nouns_with_definition[noun.lower()] =\
            nouns_with_definition.get(noun.lower(), "") + definition
    elif " n. " in line:  # word has only one definition, which is a noun:
        noun = line.split(" n. ")[0].strip()
        noun = re.sub(r"\d", "", noun)  # remove digits from noun (e.g. "Date2")
        if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
        definition = line.split(" n. ")[1].strip()
        nouns_with_definition[noun.lower()] =\
            nouns_with_definition.get(noun.lower(), "") + definition
    # skip all words / dictionary entries that are not nouns

# Now filter all the nouns from the input texts and
#   print them together with their definition and ontology links:

# First, generate all noun candidates from the input text (a noun may consist of multiple words!):
noun_candidates = []
words = input_text.split()
# remove all non-word chars, otherwise "Restaurants:" will
#   be a word but not recognized because of the ":" symbol:
words = [re.sub(r"\W", "", word) for word in words]
# longer noun candidates first (e.g. "credit card" before "credit" and "card"):
for word_length in range(len(words), 0, -1):
    for index in range(0, len(words) - word_length + 1):
        noun_candidates.append(" ".join(words[index:index+word_length]))
# print("noun_candidates = " + str(noun_candidates))

# Second, try to find all these noun candidates in the dictionary:
successful_matches = []
successful_dict_matches_with_ontology_links = OrderedDict([])
for noun_candidate in noun_candidates:
    if any(map(lambda sm: noun_candidate in sm, successful_matches)):
        # e.g. "credit" but "credit card" has already been matched before
        continue
        # a side effect of this is:
        #   "I" won't be matched anymore either because "credit card" contains an "i"

    dictionary_match = ""
    if noun_candidate.lower() in nouns_with_definition.keys():
        dictionary_match = noun_candidate.lower()
    # when the noun candidate is a plural, look up the singular in the dictionary:
    elif noun_candidate.lower()[-3:] == "ies" and noun_candidate.lower()[:-3] + "y"\
            in nouns_with_definition.keys():
        dictionary_match = noun_candidate.lower()[:-3] + "y"
    elif noun_candidate.lower()[-1] == "s" and noun_candidate.lower()[:-1]\
            in nouns_with_definition.keys():
        dictionary_match = noun_candidate.lower()[:-1]

    if dictionary_match != "":  # successful match in dictionary:
        successful_matches.append(noun_candidate)  # e.g. add "credit card" to successful matches

        # Query Wikidata with the noun found to get candidates for
        #   possible matching ontology entries:
        ontology_links = get_wikidata_entry_candidates(dictionary_match)
        # Heuristic: keep only the first N results:
        ontology_links = ontology_links[:HEURISTIC_ONLY_FIRST_N_RESULTS] 
        successful_dict_matches_with_ontology_links[dictionary_match] = ontology_links
        if DEBUG: print(dictionary_match + ": " + str([_id for _id, label, descr in ontology_links]))

nouns = successful_dict_matches_with_ontology_links.keys()

if DEBUG:
    print(str(len(nouns)) + " nouns found, with a total of "\
        + str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
        + " ontology mappings: " + str(nouns))

# Now apply various **heuristics** to reduce the number of results:

# Remove other mappings for matched nouns that are synonyms:
# (this should be the first heuristic applied before any nouns are filtered out)
if HEURISTIC_SYNONYMS:
    # Consider all pairs of nouns to check if they are synonyms:
    for noun1, noun2 in [(n1, n2) for n1 in nouns for n2 in nouns]:
        ontology_ids_noun1 = successful_dict_matches_with_ontology_links[noun1]
        ontology_ids_noun2 = successful_dict_matches_with_ontology_links[noun2]
        ontology_ids_intersection = [_id for _id in ontology_ids_noun1 if _id in ontology_ids_noun2]
        if ontology_ids_intersection != []: # noun1 and noun2 are synonyms:
            # Remove all other ontology links:
            successful_dict_matches_with_ontology_links[noun1] = ontology_ids_intersection
            successful_dict_matches_with_ontology_links[noun2] = ontology_ids_intersection
    if DEBUG:
        print(str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings left after having applied synonym heuristic.")

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
    if DEBUG:
        print(str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings left after having applied word blacklist heuristic.")

# For the upcoming heuristics, we need the properties of all the Wikidata ontology links:
all_ontology_ids =\
    [ontology_id for noun, ontology_links in successful_dict_matches_with_ontology_links.items()\
    for ontology_id, ontology_label, ontology_description in ontology_links]
wikidata_properties =\
    {ontology_id : get_wikidata_properties(ontology_id) for ontology_id in all_ontology_ids}

# Remove ontology mappings to movies, TV series, paintings and bands (musical groups).
# Use the P31 ("instance of") property for that:
if HEURISTIC_FILTER_OUT_MOVIES_ETC:
    class_blacklist = ["Q11424", "Q5398426", "Q3305213", "Q215380"]
    successful_dict_matches_with_ontology_links =\
        OrderedDict([(noun,\
        list(\
            filter(\
                lambda ontology_link:\
                    wikidata_properties[ontology_link[0]].get("P31", "") not in class_blacklist,\
                ontology_links\
            )\
        ))\
        for noun, ontology_links in successful_dict_matches_with_ontology_links.items()])
    if DEBUG:
        print(str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings left after having applied movie, TV series, etc. heuristic.")

# Try to remove subjects (e.g. China) by only keeping classes.
# Use the P279 ("subclass of", i.e. "next higher class or type") property for that:
if HEURISTIC_ONLY_KEEP_CLASSES:
    successful_dict_matches_with_ontology_links =\
        OrderedDict([(noun,\
        list(\
            filter(\
                lambda ontology_link:\
                    "P279" in wikidata_properties[ontology_link[0]],\
                ontology_links\
            )\
        ))\
        for noun, ontology_links in successful_dict_matches_with_ontology_links.items()])
    if DEBUG:
        print(str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings left after having"\
            + " removed everything that is not a subclass of sth.")

# Filter out ontology mappings that are subclasses of other ontology mappings.
# Use the P279 ("subclass of", i.e. "next higher class or type") property for that:
if HEURISTIC_USE_SUPERTYPES_ONLY:
    all_ontology_ids =\
    [ontology_id for noun, ontology_links in successful_dict_matches_with_ontology_links.items()\
    for ontology_id in ontology_links]

    successful_dict_matches_with_ontology_links =\
        OrderedDict([(noun,\
        list(\
            filter(\
                lambda ontology_link:\
                    wikidata_properties[ontology_link[0]].get("P279", "") not in all_ontology_ids,\
                ontology_links\
            )\
        ))\
        for noun, ontology_links in successful_dict_matches_with_ontology_links.items()])

    if DEBUG:
        print(str(sum([len(lst) for lst in successful_dict_matches_with_ontology_links.values()]))\
            + " ontology mappings left after having applied supertype-only heuristic.")

# Use the nltk library to *try* to generate a natural language parse for the input
# text and filter out non-nouns that could not be recognized as non-nouns using
# the naive dictionary approach, e.g. "indicative": 
if HEURISTIC_FILTER_OUT_NON_NOUNS_USING_NLTK:
    pass # ToDo

# At last, after having applied all heuristics, sort the remaining results and
# print them.
# Word frequency, original result order and ontology index are used for sorting.

def word_frequency(word):
    return input_text.lower().count(word.lower())

# First, sort the nouns by how often they appear in the input text:
successful_dict_matches_with_ontology_links =\
    OrderedDict(\
        sorted(\
            successful_dict_matches_with_ontology_links.items(),\
            key=lambda pair: word_frequency(pair[0])\
        )\
    )

# Second, we have to put all ontology links Q1, Q2, ... into a 1-dimensional list somehow:
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
# (3) using the (inverse) Cantor pairing function: [Q1, Q2, Q6, Q3, Q7, Q11, Q4, Q8, ...]
# * We will not use method (1) since it will put the least-likely search results too early.
# * We will use method (2) when all nouns occur with approximately the same frequency.
# * We will use method (3) when some nouns are much more common than other nouns.

results = [] # output to be printed; triples of (_id, label, description)

word_frequency_of_most_frequent_word =\
    word_frequency(list(successful_dict_matches_with_ontology_links.keys())[0])
word_frequency_of_least_frequent_word =\
    word_frequency(list(successful_dict_matches_with_ontology_links.keys())[-1])
# If all nouns occur with approximately the same frequency:
if word_frequency_of_most_frequent_word - word_frequency_of_least_frequent_word <= 1:
    # Use method (2):
    if DEBUG: print("Nouns occur with approx. the same frequency: list top-to-bottom...")
    # left-to-right:
    for x in range(0, max(\
        [len(ontology_links_for_yth_noun) for ontology_links_for_yth_noun\
        in successful_dict_matches_with_ontology_links.values()]\
        )):
        # top-to-bottom:
        for y in range(0, len(successful_dict_matches_with_ontology_links)):
            ontology_links_for_yth_noun =\
                list(successful_dict_matches_with_ontology_links.items())[y][1]
            if x < len(ontology_links_for_yth_noun):
                results += [ontology_links_for_yth_noun[x]]
else: # Some nouns are much more common than other nouns:
    # Use method (3):
    if DEBUG: print("Some nouns are much more comman than others: list Cantor-like...")
    total_number_of_ontology_links =\
        sum(map(\
            lambda lst: len(lst), successful_dict_matches_with_ontology_links.values()\
        ))
    i = 0
    while len(result) < total_number_of_ontology_links:
        x, y = inverse_cantor_pairing_function(i)
        if y < len(successful_dict_matches_with_ontology_links.items())\
           and x < len(list(successful_dict_matches_with_ontology_links.items())[y][1]):
            result += list(successful_dict_matches_with_ontology_links.items())[y][1][x]
        i += 1

# # Method (1) would have looked like this:
# results = successful_dict_matches_with_ontology_links.values()
# # Now we have a list of lists, so flatten it:
# results = [x for xs in results for x in xs]

# Remove duplicates (duplicates exist when the text contained synonyms):
results = list(OrderedDict.fromkeys(results))

# Third, put additional weights on results with a very high ontology index.
# (E.g. Q11666766 (restaurant; type of business under Japan's Food Sanitation Law))
if HEURISTIC_USE_ONTOLOGY_INDEXES:
    ontology_indexes = [int(_id[1:]) for _id, label, description in results]
    # (the [1:] strips the "Q" prefix that each Wikidata entry has)
    average_ontology_index = statistics.mean(ontology_indexes)
    ontology_index_standard_deviation = statistics.stdev(ontology_indexes)
    # Put additional weights on ontology entries with whose index is more than X
    #   standard deviations away from the mean/average:
    # ToDo => implement/keep/remove/deactivate this feature?!

if DEBUG: print("")  # separator

# At last, print the result:
for _id, label, description in results:
    print(_id + " (" + label + "; " + description + ")")
