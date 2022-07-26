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
  - ... (see --help)
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
		[(weight1 * dct1.get(wi, 0.0) +\
		 weight2 * dct2.get(wi, 0.0) +\
		 weight3 * dct3.get(wi, 0.0),\
		 wi) for wi in allWikidataItems]
	sort(result, key=lambda tuple: tuple[0], reverse=True)
	return result

class Table:
	def __init__(self, surroundingText: str, headerRow: List[str],\
				 columns: List[List[str]]):
		"""
		Initalize a new Table that has already been parsed.
		"""

		self.surroundingText = surroundingText  # (1) Using Textual Surroundings
		self.headerRow = headerRow  # (2) Using Attribute Names
		self.columns = columns  # (3) Using Attribute Extensions

	def pretty_print(self, maxNumberOfTuples=6, maxColWidth=25) -> str:
		"""
		A pretty printable version of this Table, e.g.:

		Restaurant Name       | Rating | Price | Reviews
		------------------------------------------------
		Aquarius              |        | $$    | 0
		BIG & little’s        |        | $     | 0
		Brown Bag Seafood Co. |        | $$    | 0
		...                   | ...    | ...   | ...

		(in this example, maxNumberOfTuples=3)
		"""

        # The width (number of characters) of each column, only regarding
        #   the first `maxNumberOfTuples` rows each:
		columnWidths: List[int] = list(map(\
			lambda column: max(map(\
				lambda cell: len(cell),\
				column[0:maxNumberOfTuples]\
			)),\
			self.columns\
			))
		# If a header name is longer than corresponding column width, it
		#   has to be increased further:
		columnWidths = list(\
			map(\
				lambda tuple: max(tuple[0], tuple[1]),\
				zip(columnWidths, map(lambda header: len(header),\
					self.headerRow))\
				)\
			)
		# Every column shall have a width of at least 3:
		columnWidths = [max(3, cw) for cw in columnWidths]
		# Every column shall have a width of at most `maxColWidth`:
		columnWidths = [min(maxColWidth, cw) for cw in columnWidths]

		def print_row(cells: List[str], widths: List[int]) -> str:
			res: str = ""
			for i in range(0, len(cells)):
				width = widths[i]
				res += cells[i][:width] + " " * (width-len(cells[i]))
				if i != len(cells)-1: res += " | "
			res += "\n"
			return res

		result: str = ""

		result += print_row(self.headerRow, columnWidths)

		totalWidth = sum(columnWidths) + 3*(len(columnWidths)-1)
		result += "-" * totalWidth + "\n" # "-----------------------------"

		for y in range(0, min(maxNumberOfTuples, len(self.columns[0]))):
			result += print_row(\
				[self.columns[x][y] for x in range(0, len(self.columns))],\
				 columnWidths)

		if maxNumberOfTuples < len(self.columns[0]):  # print "... | ..." row:
			result += print_row(["..."] * len(columnWidths), columnWidths)

		return result

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
		pass  # ToDo: filter_nouns_with_heuristics.py

	def classifyUsingAttrNames(self) -> Dict[WikidataItem, float]:
		pass  # ToDo: attr_names_to_ontology_class.py

	def classifyUsingAttrExtensions(self) -> Dict[WikidataItem, float]:
		pass  # ToDo: attr_extension_to_ontology_class.py

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

# A small default table corpus (consisting of the 7 tables also used as
#   examples throughout my paper) to be used when no table corpus is supplied.
# Useful for testing.
defaultTableCorpusWithCorrectMappings: List[Tuple[Table, WikidataItem]] =\
	[ # ToDo: surrounding texts and Wikidata mappings
	(
		Table(
			surroundingText=\
			"Properties of different car models, from 1970 to 1982.",
			headerRow=["mpg", "cylinders", "displacement", "horsepower",\
			"weight", "acceleration", "model year", "origin", "car name"],
			columns=[\
			["18.0", "15.0", "18.0"],\
			["8", "8", "8"],\
			["307.0", "350.0", "318.0"],\
			["130.0", "165.0", "150.0"],\
			["3504.", "3693.", "3436."],\
			["12.0", "11.5", "11.0"],\
			["70", "70", "70"],\
			["1", "1", "1"],\
			["\"chevrolet chevelle malibu\"", "\"buick skylark 320\"",\
			"\"plymouth satellite\""]\
			]\
		),
		WikidataItem(
			entity_id="Q3231690",
			label="automobile model",
			description="""industrial automobile model associated with a brand,
			defined usually from an engineering point of view by a combination
			of chassis/bodywork"""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Country", "Project Name", "Types of Assistance",\
			"Approval Number/s", "Status", "Approval Date"],
			columns=[\
			["Nepal", "Pakistan", "India", "India"],\
			["30232-013 Decentralized Rural Infrastructure and Livelihoods",\
			"""38135-013 Multisector Rehabilitation Project for Azad Jammu &
			Kashmir""",
			"35335-013 National Highway Sector II",
			"""38136-013 Multi-sector Project for Infrastructure Rehabilitation
			in Jammu and Kashmir"""],\
			["Loan", "Loan", "Loan", "Loan"],
			["2092", "2153", "2154", "2151"],
			["Closed / Terminated", "Closed / Terminated",\
			"Closed / Terminated", "Closed / Terminated"],
			["23 Dec 2004", "21 Dec 2004", "21 Dec 2004", "21 Dec 2004"]\
			]\
		),
		WikidataItem(
			entity_id="Q170584",
			label="project",
			description="""collaborative enterprise, frequently involving
			research or design, that is carefully planned to achieve a
			particular aim"""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Name", "Yr", "Pos", "G", "Rec.", "Yards", "Avg.",\
			"TD", "Rec./G", "Yards/G"],
			columns=[\
			["Jordan James", "Keevan Lucas", "Trey Watts", "Thomas Roberson"],\
			["SR", "FR", "SR", "JR"],\
			["WR", "WR", "RB", "WR"],\
			["11", "12", "12", "8"],\
			["39", "32", "46", "27"],\
			["471", "442", "395", "363"],\
			["12.08", "13.81", "8.59", "13.44"],\
			["2", "1", "1", "4"],\
			["3.5", "2.7", "3.8", "3.4"],\
			["42.8", "36.8", "32.9", "45.4"]\
			]\
		),
		WikidataItem(
			entity_id="",  # ToDo: "player" or ... ?!
			label="",
			description=""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Restaurant Name", "Rating", "Price", "Reviews"],
			columns=[\
			["""1Aquarius2459 N Pulaski Rd |
			At W Altgeld St Order From This Restaurant""",\
			"""2BIG & little’s1034 W Belmont Ave |
			At N Kenmore Ave Order From This Restaurant""",\
			"""3Brown Bag Seafood Co.340 E Randolph St |
			Btwn N Columbus & N Lake Shore Dr""",\
			"""4Captain Hook’s Fish & Chicken8550 S Cottage Grove Ave |
			Btwn E 85th & 86th St"""],\
			["", "", "", ""],\
			["$$", "$", "$$", "$"],\
			["0", "0", "0", "14"]
			]\
		),
		WikidataItem(
			entity_id="Q11707",
			label="restaurant",
			description="""single establishment which prepares and serves food,
			located in building"""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Name", "Status", "County",\
			"Population Census 1990-04-01", "Population Census 2000-04-01",\
			"Population Census 2010-04-01"],
			columns=[\
			["Mound Station", "Mount Sterling", "Ripley", "Versailles"],\
			["Village", "City", "Village", "Village"],\
			["Brown", "Brown", "Brown", "Brown"],\
			["147", "1,994", "75", "480"],\
			["124", "2,085", "105", "569"],\
			["122", "2,025", "86", "478"]
			]
		),
		WikidataItem(
			entity_id="",  # ToDo: "location" or ... ?!
			label="",
			description=""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Song Title", "Year Released *", "Song Rank"],
			columns=[\
			["The Stroke", "LONELY IS THE NIGHT", "Everybody Wants You",\
			"My Kinda Lover", "In The Dark", "TOO DAZE GONE",\
			"THE BIG BEAT", "Rock Me Tonite", "Emotions In Motion",\
			"Don’t Say You Love Me"],\
			["1905", "1905", "1905", "1905", "1905",\
			"1905", "1905", "1905", "1905", "1905"],\
			["17,063", "32,018", "46,267", "54,751", "67,138",\
			"69,396", "171,132", "106,024", "158,701", "179,474"]\
			]\
		),
		WikidataItem(
			entity_id="",  # ToDo: "song" or "musical work" ?!
			label="",
			description=""
		)
	),
	(
		Table(
			surroundingText="",
			headerRow=["Name", "School", "Year", "Descendants"],
			columns=[\
			["Richard Battin", "David Benney",\
			"Peter Chiarulli", "Alfred Clark"],\
			["Massachusetts Institute of Technology",\
			"Massachusetts Institute of Technology",\
			"Brown University",\
			"Massachusetts Institute of Technology"],\
			["1951", "1959", "1949", "1963"],\
			["", "158", "", ""]\
			]\
		),
		WikidataItem(
			entity_id="Q48282",
			label="student",
			description="""learner, or someone who attends an educational
			institution"""
		)
	)
	]

def main():
	parser = argparse.ArgumentParser(
		description="NETT - Narrative Entity Type(s) to Tables")

	parser.add_argument(
    	'entityTypes',
    	type=str,
    	help="""A list of entity types.
    	Ideally they're Wikidata ID's of the form 'Q000000',
    	otherwise they're strings automatically mapped to Wikidata ID's.
    	Normally they're the entity types to look for.
    	When the --stats flag is supplied however, they are interpreted as
    	the correct entity types for the tables in the corpus (when the corpus
    	folder is read in alphabetical order).
    	When no entity types are supplied at all, a ranked list of entity types
    	is returned for every table in the corpus instead.""",
    	nargs='*',
    	metavar='TYPE')

	parser.add_argument('--stats',
		action='store_true',
		help="""Interpret the supplied entity types not as those to search for
		but rather as the correct mappings for the tables in the corpus.
		The tables in the corpus are still classfied but based on the given
		correct mappings, statistics are returned instead.
		Statistics include mean reciprocal rank (MRR), top-k coverage
		and recall.
		When no entity types a supplied and another corpus than the small
		default one is being used, the user will be asked interactively for
		the correct mapping for every table! This is very useful for evaluating
		this tool!""")

	parser.add_argument('-k',
    	type=int,
    	default=1,
    	help="""Only return tables for which the entity type searched for was
    	in the top-k results. By default, k=1 which means that only tables are
    	returned for which the entity type searched for was the best guess.""",
    	metavar='K')

	parser.add_argument('--threshold',
    	type=float,
    	default=0.0,
    	help="""Only return tables for which the entity type searched for got
    	a score of at least this threshold (floating-point number).
    	This makes sense particularly when used together with the --normalize
    	flag. When --normalize is set and all weights are kept at their default
    	value of 1.0, then this value shall be somewhere between 0.0 and 3.0.
    	This is a filter that is set in addition to the -k filter!""",
    	metavar='THRESHOLD')

	parser.add_argument('--dont-use-textual-surroundings',
		action='store_true',
		help="""Do not take textual surroundings of tables into account.
		This only has an effect for JSON input.""")

	parser.add_argument('--dont-use-attr-names',
		action='store_true',
		help='Do not take the attribute/column names of tables into account.')

	parser.add_argument('--dont-use-attr-extensions',
		action='store_true',
		help='Do not take attribute extensions of tables into account.')

	parser.add_argument('--normalize',
		action='store_true',
		help="""Whether to normalize the result of each of the 3
    	approaches into the [0,1] range""")

	parser.add_argument('--textual-surroundings-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the textual surroundings approach.',
    	metavar='WEIGHTING')

	parser.add_argument('--attr-names-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the attribute names approach.',
    	metavar='WEIGHTING')

	parser.add_argument('--attr-extensions-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the attribute extensions approach.',
    	metavar='WEIGHTING')

	# (Advanced) ToDo: if all weights are set to 0.0 try out ("learn") which
	#   weights lead to the best results!

	parser.add_argument('--corpus',
    	type=str,
    	default='',
    	help="""Path to a folder containing tables as CSV/JSON/TAR files.
    	Or path to a single TAR file containing tables as CSV/JSON files.
    	If not specified, a small default corpus is being used.
    	Note that all tables smaller than 3x3 are rigorously filtered out.
    	Folders are parsed in alphabetical order.""",
    	metavar='PATH')

	parser.add_argument('--ordered',
		action='store_true',
		help="""When this flag is set, the tables in the output are sorted by
		how well they score. Beware that lazy output is lost which means that
		this flag should not be used together with a very big corpus!""")

	parser.add_argument('--verbose', '-v',
		action='store_true',
		help='Print verbose info prints to stderr.')

	parser.add_argument('--debug',
		action='store_true',
		help='Print debug info prints to stderr.')

	# cf. https://stackoverflow.com/questions/7869345/
	#     how-to-make-python-argparse-mutually-exclusive-
	#     group-arguments-without-prefix:
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--jaccard', action='store_true',
		help="Use Jaccard index for word similarity of column/attribute names.")
	group.add_argument('--sbert', action='store_true', default=True,
		help="Use SBERT for word similarity of column/attribute names.")

	args = parser.parse_args()

	corpus: str = args.corpus
	stats: bool = args.stats
	entityTypes: List[str] = args.entityTypes

	if corpus == "" and stats and entityTypes == []:
		# Give statistics for the default corpus without looking for any
		#   specific entity types:
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus == "" and stats and entityTypes != []:
		# Give statistics for the default corpus, in general and also specific
		#  to the entity types mentioned:
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus == "" and not stats and entityTypes == []:
		# Return a ranked list of entity candidates for every table in the
		#   default corpus:
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus == "" and not stats and entityTypes != []:
		# Return all the tables from the default corpus believed to represent
		#   one of the given entity types (of course even though we already
		#   know the correct mappings for the default corpus): 
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus != "" and stats and entityTypes == []:
		# Main Feature #1:
		#   Non-default corpus without correct entity type mappings supplied as
		#     parameters, program has to ask user for every table which mapping
		#     is correct:
		print("This combination of parameters is not yet implemented.")  # ToDo!
		# -> use pretty_print() as ask user for correct mapping for each table
		# -> the user enters "1", "2", "3", ..., "X", "N/A", or "finish"
	elif corpus != "" and stats and entityTypes != []:
		# Give statistics for a given corpus, the correct entity type mappings
		#   are supplied (in alphabetical order).
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus != "" and not stats and entityTypes == []:
		# Map all tables of the given corpus to the top-k entities:
		print("This combination of parameters is not yet implemented.")  # ToDo
	elif corpus != "" and not stats and entityTypes != []:
		# Main Feature #2:
		#   Search the corpus for tables whose tuples represent one
		#     of the given entity types:
		print("This combination of parameters is not yet implemented.")  # ToDo!


if __name__ == "__main__":
	main()
