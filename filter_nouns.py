import sys
import os
from os.path import exists
from itertools import takewhile
import urllib.parse
import json
from urllib.request import urlopen
import re  # regex


def get_wikidata_entry_candidates(search_string):
    api_url = \
        "https://www.wikidata.org/" \
        "w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search="\
        + urllib.parse.quote_plus(search_string)
    json_result = urlopen(api_url).read().decode('utf-8')
    parsed_json = json.loads(json_result)

    # Return id, label and description:
    return list(
        map(
            lambda list_el:
                list_el["id"] +
                " (" + list_el.get("label", "") + "; " +
                list_el.get("description", "") + ")",
            parsed_json["search"]
        )
    )


input_text = sys.argv[1]  # the text to filter for nouns
NO_WIKIDATA = (len(sys.argv) >= 3 and sys.argv[2] == "--no-wikidata")

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
        noun = re.sub(r"\(.*\)", "", noun).strip()  # e.g. "Program  (brit. Programme)"=>"Program"
        if len(noun) <= 2: continue  # ignore nouns with 1 or 2 letters
        # the noun definition is everything after the first "—n." and before the next "—":
        definition = line.split(" —n. ")[1].split("—")[0].strip()
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
print("")  # print an initial empty line as a separator
successful_matches = []
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

        print(noun_candidate)
        print(nouns_with_definition[dictionary_match])
        if not NO_WIKIDATA:
            ontology_link = get_wikidata_entry_candidates(dictionary_match)
            print(ontology_link)
        print("")  # print empty line as separator
