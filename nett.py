"""
NETT = Narrative Entity Type(s) to Tables

This program takes as input:
* a corpus of relational tables, either in CSV or in a specific JSON format
  (the files are allowed to be inside one or multiple .tar archives);
  when no corpus is specified a small default corpus is being used
  => note that all tables smaller than 3x3 are rigorously filtered out
* - EITHER: a list of one or more entity types occuring in the narrative that
    is to be grounded (ideally as Wikidata ID's, otherwise as literal strings)
    => you may also supply ids/names of entities instead of entity types,
       in that case they are simply resolved to the entity type they're an
       instance of and the output tables restricted to those containing a
       string equal or similar to that entity's name
  - OR: optionally the list of correct mappings for the given corpus
        (supplied automatically when the default corpus is being used)
  - when NEITHER of the two is supplied, a ranked list of entity candidates
    for every table in the corpus is returned
* various settings as parameters:
  - ...
  - whether the output tables shall be ordered (--ordered) by how well they fit
    (lazy outputting is lost in that case!)
  - whether to use Jaccard (--jaccard) or SBERT (--sbert) for word similarity
  - whether to activate verbose info prints (-v or --verbose)
  - whether to activate debug prints (--debug)

When a list of one or more entity types is supplied, it produces as output:
* for each input entity type an ordered (or unordered) list of relational
  tables from the given corpus for which the program thinks that the tuples
  represent entities of that entity type
* the output is (lazily if unorderd) printed to stdout in JSON format

When a list of correct mappings was given as input, the output is instead:
* statistics
  - the MRR (mean reciprocal rank)
  - the top-k coverage for k=1,2,...,100
    (k can be supplied as a parameter too, using -k)
  - the recall for all classes/entity types occurring in the supplied list
    (sorted)

When neither of those is supplied, it returns a ranked list of entity type
  candidates for every table in the corpus.
"""

from __future__ import annotations
from typing import List, Dict, Any, Iterator
import json
import argparse

def normalize(dct: Dict[WikidataItem, float])\
	-> Dict[WikidataItem, float]:
	if dct is not None:
		min_value: float = min(dct.values())
		max_value: float = max(dct.values())
		return {w: (f - min_value) / (max_value - min_value)\
				for w, f in dct.items()}
	else:
		return None

def combine3(dct1: Dict[WikidataItem, float], weight1: float,\
			dct2: Dict[WikidataItem, float], weight2: float,\
			dct3: Dict[WikidataItem, float], weight3: float)\
			-> List[Tuple[float, WikidataItem]]:
	allWikidataItems = set(dct1.keys())\
						.union(set(dct2.keys()))\
						.union(set(dct3.keys()))
	result: List[Tuple[float, WikidataItem]] =\
		[weight1 * dct1.get(wi, 0.0) +\
		 weight2 * dct2.get(wi, 0.0) +\
		 weight3 * dct3.get(wi, 0.0),\
		 wi for wi in allWikidataItems]
	sort(result, key=lambda tuple: tuple[0], reverse=True)
	return result

class Table:
	def __init__(self, surroundingText="", headerRow: List[str],\
				 columns: List[List[str]]):
		"""
		Initalize a new Table that has already been parsed.
		"""

		self.surroundingText = surroundingText  # (1) Using Textual Surroundings
		self.headerRow = headerRow  # (2) Using Attribute Names
		self.columns = columns  # (3) Using Attribute Extensions

	def classify(self,\
				 useTextualSurroundings=True, textualSurroundingsWeighting=1.0,\
				 useAttrNames=True, attrNamesWeighting=1.0,\
				 useAttrExtensions=True, attrExtensionsWeighting=1.0,\
				 normalizeApproaches=False)\
				-> List[Tuple[float, WikidataItem]]:
		"""
		Classify this table semantically.
		Returns an ordered list of WikidataItems that might represent the entity
		type of the tuples of this table, each with a floating-point score
		indicating how well it fits the table.
		
    	Keyword arguments:
    	useTextualSurroundings -- whether to use approach #1 if possible
    	                          (default True)
    	textualSurroundingsWeighting -- how to weight approach #1
    	                                (default 0.0)
    	useAttrNames -- whether to use approach #2 if possible
    	                (default True)
    	attrNamesWeighting -- how to weight approach #1
                              (default 0.0)
    	useAttrExtensions -- whether to use approach #3 if possible
    	                     (default True)
    	attrExtensionsWeighting -- how to weight approach #1
    	                           (default 0.0)
    	normalizeApproaches -- whether to normalize the result of each of the 3
    	                       approaches into the [0,1] range
    	                       (default False)

		More about `normalizeApproaches`:

    	Whether to normalize the rankings of classifyUsingTextualSurroundings(),
	    classifyUsingAttrNames(), classifyUsingAttrExtensions() into the same
	    range, i.e. the interval [0,1].
	 
	    When normalizeApproaches == False, the final ranking of classify()
	    is computed as:
	    classify() =
	        TEXTUAL_SURROUNDINGS_WEIGHTING * classifyUsingTextualSurroundings()
	      + ATTR_NAMES_WEIGHTING * classifyUsingAttrNames()
	      + ATTR_EXTENSIONS_WEIGHTING * classifyUsingAttrExtensions()
	 
	    When normalizeApproaches == True, the final ranking of classify()
	    is computed as:
	    classify() =
	        TXT_SURR_WGHT * normalize(classifyUsingTextualSurroundings())
	      + ATTR_NAMES_WEIGHTING * normalize(classifyUsingAttrNames())
	      + ATTR_EXTENSIONS_WEIGHTING * normalize(classifyUsingAttrExtensions())
	    => Advantage:
	       The weightings truly reflect the contribution of each approach.
	    => Disadvantage:
	       The information that one approach might be more confident than
	       another approach is lost.
    	"""

		resultUsingTextualSurroundings: Dict[WikidataItem, float] = {}
		if useTextualSurroundings and self.surroundingText != "":
			resultUsingTextualSurroundings =\
				self.classifyUsingTextualSurroundings()

		resultUsingAttrNames: Dict[WikidataItem, float] = {}
		if useAttrNames and self.headerRow != []:
			resultUsingAttrNames = self.classifyUsingAttrNames()

		resultUsingAttrExtensions: Dict[WikidataItem, float] = {}
		if useAttrExtensions and self.columns != []:
			resultUsingAttrExtensions = self.classifyUsingAttrExtensions()

		if normalizeApproaches:
			resultUsingTextualSurroundings =\
				normalize(resultUsingTextualSurroundings)
			resultUsingAttrNames = normalize(resultUsingAttrNames)
			resultUsingAttrExtensions = normalize(resultUsingAttrExtensions)

		combinedResult: List[Tuple[float, WikidataItem]] = []

		combinedResult = combine3(\
			dct1=resultUsingTextualSurroundings,\
			weight1=textualSurroundingsWeighting,\
			dct2=resultUsingAttrNames,\
			weight2=attrNamesWeighting,\
			dct3=resultUsingAttrExtensions,\
			weight3=attrExtensionsWeighting,\
		)

		return combinedResult

	def classifyUsingTextualSurroundings(self) -> Dict[WikidataItem, float]:
		pass  # ToDo

	def classifyUsingAttrNames(self) -> Dict[WikidataItem, float]:
		pass  # ToDo

	def classifyUsingAttrExtensions(self) -> Dict[WikidataItem, float]:
		pass  # ToDo

	@classmethod
	def parseCSV(csv: str) -> Table:
		pass  # ToDo

	@classmethod
	def parseJSON(json: str) -> Table:
		pass  # ToDo

	@classmethod
	def parseTAR(path: str) -> Iterator[Table]:
		pass  # ToDo

	@classmethod
	def parseFolder(path: str) -> Iterator[Table]:
		pass  # ToDo (use "yield")

dbpediaClassesMappedToWikidata: Dict[str, str] =\
	{
	# ToDo: generate using another script
	}

dbpediaPropertiesMappedToSBERTvector: Dict[str, Any] =\
	{
	# ToDo: generate using another script
	}

# A small default table corpus to be used when no table corpus is supplied.
# Useful for testing.
defaultTableCorpusWithCorrectMappings: List[Tuple[Table, WikidataItem]] =\
	[
	# ToDo
	]

def main():
	parser = argparse.ArgumentParser(description="NETT")
	# ToDo: argparse
	args = parser.parse_args()

	# ToDo: program

if __name__ == "__main__":
	main()
