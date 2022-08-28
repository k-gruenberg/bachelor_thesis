"""
NETT = Narrative Entity Type(s) to Tables

This program takes as input:
* a corpus of relational tables, either in CSV (or Excel)
  or in a specific JSON format
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
import json  # https://docs.python.org/3/library/json.html
import argparse
import re
import os
import sys
import csv  # https://docs.python.org/3/library/csv.html
import tarfile  # https://docs.python.org/3/library/tarfile.html
import tempfile  # https://docs.python.org/3/library/tempfile.html

from numpy import transpose

from WikidataItem import WikidataItem

# Import the fundamental approaches
#     #1 "Using Textual Surroundings"
#     #2 "Using Attribute Names"
#     #3 "Using Attribute Extensions"
# from the respective Python files:
from filter_nouns_with_heuristics import filter_nouns_with_heuristics_as_dict
from attr_names_to_ontology_class import attr_names_to_ontology_class
from attr_extension_to_ontology_class import attr_extension_to_ontology_class

from nett_map_dbpedia_classes_to_wikidata import\
	get_dbpedia_classes_mapped_to_wikidata
from nett_map_dbpedia_properties_to_sbert_vectors import\
	get_dbpedia_properties_mapped_to_SBERT_vector

DEBUG = True

dbpediaClassesMappedToWikidata: Dict[str, str] = None
dbpediaPropertiesMappedToSBERTvector: Dict[str, Any] = None
# => these 2 are only set in the main() so that calling "--help" isn't
#    unnecessarily slowed down

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

		If the `columns` haven't been parsed for a `headerRow` yet,
		set headerRow=[] and
		call the parse_header_row() method after construction!

		`headerRow` may be `[]` but never `None`!
		"""

		self.surroundingText = surroundingText  # (1) Using Textual Surroundings
		self.headerRow = headerRow  # (2) Using Attribute Names
		self.columns = columns  # (3) Using Attribute Extensions

	def width(self) -> int:
		"""
		Returns the width of this Table, i.e. the number of columns.
		"""
		return len(self.columns)  # width == # of columns

	def min_height(self, includingHeaderRow=True) -> int:
		"""
		Returns the height of this Table, i.e. the number of rows.
		Including the header row by default (if this Table has one, that is).
		Set includingHeaderRow=False to exclude a possible header row.

		The value returned is different to that of max_height() only if
		the columns don't all have the same height, which they should have.
		"""
		return min(len(col) for col in self.columns) +\
			(1 if includingHeaderRow and self.headerRow != [] else 0)

	def max_height(self, includingHeaderRow=True) -> int:
		"""
		Returns the height of this Table, i.e. the number of rows.
		Including the header row by default (if this Table has one, that is).
		Set includingHeaderRow=False to exclude a possible header row.

		The value returned is different to that of min_height() only if
		the columns don't all have the same height, which they should have.
		"""
		return max(len(col) for col in self.columns) +\
			(1 if includingHeaderRow and self.headerRow != [] else 0)

	def pretty_print(self, maxNumberOfTuples=6, maxColWidth=25) -> str: # ToDo: what if self.headerRow == [] ?!
		"""
		A pretty printable version of this Table, e.g.:

		Restaurant Name       | Rating | Price | Reviews
		------------------------------------------------
		Aquarius              |        | $$    | 0
		BIG & little's        |        | $     | 0
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
		if self.headerRow != []:
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

		if self.headerRow != []:
			result += print_row(self.headerRow, columnWidths)
		else:  # no header row to print => print empty header row:
			result += print_row([""] * len(columnWidths), columnWidths)

		totalWidth = sum(columnWidths) + 3*(len(columnWidths)-1)
		result += "-" * totalWidth + "\n" # "-----------------------------"

		for y in range(0, min(maxNumberOfTuples, len(self.columns[0]))):
			result += print_row(\
				[self.columns[x][y] for x in range(0, len(self.columns))],\
				 columnWidths)

		if maxNumberOfTuples < len(self.columns[0]):  # print "... | ..." row:
			result += print_row(["..."] * len(columnWidths), columnWidths)

		return result


	def as_csv(self, with_header=True, max_number_of_rows: int = -1) -> str:
		if not with_header:
			self_min_height: int = self.min_height(includingHeaderRow=False)
			if max_number_of_rows == -1:
				max_number_of_rows = self_min_height
			self_as_csv: str = ""
			for row_index in range(0, min(max_number_of_rows, self_min_height)):
				self_as_csv += ",".join(\
					self.columns[col_index][row_index]\
					for col_index in range(0, self.width())) + "\n"
			return self_as_csv
		else:
			return None  # ToDo

	def parse_header_row(self) -> bool:
		"""
		When self.headerRow == []:
		    Tries to to identify a header row in self.columns using the
		    heuristic used by the csv.Sniffer().has_header() method
		    (cf. https://docs.python.org/3/library/csv.html).
		    If found, the header row is deleted from self.columns and
		    self.headerRow is set instead.
		    Returns True when a header row was found and False otherwise.
		When self.headerRow != []:
		    This method does nothing and returns True.

		Important note:
		When using one of the parseXXX() class methods,
		calling this function is NOT necessary!!
		"""
		if self.headerRow == []:
			self_as_csv_sample: str =\
				self.as_csv(with_header=False, max_number_of_rows=20)
			# From https://docs.python.org/3/library/csv.html,
			# regarding csv.Sniffer.has_header(sample):
			# "Twenty rows after the first row are sampled; if more than half
			#  of columns + rows meet the criteria, True is returned."
			if csv.Sniffer().has_header(self_as_csv_sample):
				# Set the header row to the first row:
				self.headerRow = [self.columns[col_index][0] for\
					col_index in range(0, len(self.columns))]
				# Delete the header row from self.columns where it
				#   does not belong:
				for col_index in range(0, len(self.columns)):
					del self.columns[col_index][0]
				return True
			else:
				return False  # csv.Sniffer().has_header() found no header.
		else:
			return True  # There already is a header row (parsed).


	# Correctly regex-matching URLs and email addresses is actually much
	# harder than one might think, read:
	#
	# Email addresses:
	# * https://stackoverflow.com/questions/9238640/
	#     how-long-can-a-tld-possibly-be
	# * https://stackoverflow.com/questions/201323/
	#     how-can-i-validate-an-email-address-using-a-regular-expression
	# * http://www.ex-parrot.com/~pdw/Mail-RFC822-Address.html
	# * https://en.wikipedia.org/wiki/Email_address#Local-part
	# * http://emailregex.com/
	#
	# URLs:
	# * https://stackoverflow.com/questions/3809401/
	#     what-is-a-good-regular-expression-to-match-a-url
	# * https://mathiasbynens.be/demo/url-regex:

	PHONE_NUMBER_REGEX = r"\+?\d[\d -]+\d"
	URL_REGEX = r"^(https:|http:|www\.)\S*"  # https://regex101.com/r/S2CbwM/1
	EMAIL_REGEX = r".+@.+"
	#EMAIL_REGEX = r".+@.+\..+"
	# -> problem: "jsmith@[IPv6:2001:db8::1]" is a valid email without any dots!
	#EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
	# -> source: emailregex.com
	# -> problem: !#$%&'*+-/=?^_`{|}~ are allowed characters in emails too!
	NUMERIC_REGEX = r"[\+\-]?[\d., _]+"  # r"[\d.,]+"
	GEO_REGEX = r"""[\+\-\d.,;'" NESW]+"""
	LONG_REGEX = r".{50,}"

	BLACKLISTED_REGEXES: List[str] = [\
		PHONE_NUMBER_REGEX,  # matches phone numbers
		URL_REGEX,  # matches URLs
		EMAIL_REGEX,  # matches email addresses
		NUMERIC_REGEX,  # matches numeric values
		GEO_REGEX,  # matches geographic coordinates
		LONG_REGEX  # matches "long values, such as verbose descriptions"
	]  # => cf. Quercini & Reynaud "Entity Discovery and Annotation in Tables"

	BLACKLISTED_COMPILED_REGEXES =\
		[re.compile(regex_string) for regex_string in BLACKLISTED_REGEXES]

	def get_identifying_column(self) -> List[str]:  # ToDo!!!  # ToDo: what about the heuristic used by T2K Match?!
		"""
		Try to identify the identifiying columns of this table in
		  1 or 2 steps:
		
		Step 1) use uniqueness
		Step 2) if more than 1 column is unique: use regexes, more
		        precisely:
		
		Throw out columns where at least one non-empty cell content matches
		  at least one of the regexes in BLACKLISTED_COMPILED_REGEXES.
		Hopefully exactly one column will be left over.
		The idea to disregard cells whose values matches a certain regex
		  stems from Quercini & Reynaud's paper
		  "Entity Discovery and Annotation in Tables".
		"""

		identifying_column_candidates: List[List[str]] = []

		for column in self.columns:
			for cell in column:
				for pattern in BLACKLISTED_COMPILED_REGEXES:
					if pattern.fullmatch(cell) is not None:  # blacklist match
						continue  # ...means this column is not identifying
			identifying_column_candidates.append(column)

		if len(identifying_column_candidates) != 1:
			return None
		else:
			return identifying_column_candidates[0]

	def classify(self,\
				 useTextualSurroundings=True, textualSurroundingsWeighting=1.0,\
				 useAttrNames=True, attrNamesWeighting=1.0,\
				 useAttrExtensions=True, attrExtensionsWeighting=1.0,\
				 normalizeApproaches=False,
				 printProgressTo=sys.stdout)\
				-> List[Tuple[float, WikidataItem]]:  # ToDo: probably move below!
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
			print("[PROGRESS] Classifying using textual surroundings...",\
				file=printProgressTo)
			resultUsingTextualSurroundings =\
				self.classifyUsingTextualSurroundings()

		resultUsingAttrNames: Dict[WikidataItem, float] = {}
		if useAttrNames and self.headerRow != []:
			print("[PROGRESS] Classifying using attribute names...",\
				file=printProgressTo)
			resultUsingAttrNames = self.classifyUsingAttrNames()

		resultUsingAttrExtensions: Dict[WikidataItem, float] = {}
		if useAttrExtensions and self.columns != []:
			print("[PROGRESS] Classifying using attribute extensions...",\
				file=printProgressTo)
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
		"""
		Classify this table using the "Using Textual Surroundings" approach,
		implemented in filter_nouns_with_heuristics.py.
		Higher scores mean better matches.
		"""

		return filter_nouns_with_heuristics_as_dict(\
			input_text=self.surroundingText,\
			VERBOSE=False,\
			ALLOW_EQUAL_SCORES=True)

	def classifyUsingAttrNames(self, useSBERT: bool)\
		-> Dict[WikidataItem, float]:
		"""
		Classify this table using the "Using Attribute Names" approach,
		implemented in attr_names_to_ontology_class.py.
		Higher scores mean better matches.

		When useSBERT==False, the Jaccard index is used for computing
		word similarity instead.
		"""

		return attr_names_to_ontology_class(\
			inputAttrNames=self.headerRow,
			USE_BETTER_SUM_FORMULA=True,
			USE_SBERT_INSTEAD_OF_JACCARD=useSBERT,
			VERBOSE=False
			)

	def classifyUsingAttrExtensions(self, useBing=False, useWebIsAdb=False)\
		 -> Dict[WikidataItem, float]:
		"""
		Classify this table using the "Using Attribute Extensions" approach,
		implemented in attr_extension_to_ontology_class.py.
		Higher scores mean better matches.

		The `useBing` and `useWebIsAdb` parameters
		shall not both be set to True!
		"""

		if useBing:
			return None
			# ToDo: refactor attr_extension_to_ontology_class_web_search.py
		elif useWebIsAdb:
			return None  # ToDo: not even coded yet...
		else:
			return attr_extension_to_ontology_class(\
				cell_labels=self.get_identifying_column())

		# ToDo: write get_identifying_column() function !!!!!

	@classmethod
	def identifyCSVdialect(cls, csv_str: str) -> Dialect:
		return csv.Sniffer().sniff(csv_str)

	@classmethod
	def parseCSV(cls, csv_str: str, dialect: Dialect = None) -> Table:
		columns: List[List[str]] = []

		# Documentation of
		#   csv.reader(csvfile, dialect='excel', **fmtparams):
		# "csvfile can be any object which supports the iterator protocol
		#  and returns a string each time its __next__() method is called —
		#  file objects and list objects are both suitable. If csvfile is a
		#  file object, it should be opened with newline=''."

		csv_reader = csv.reader(csv_str.splitlines(keepends=True), dialect\
			if dialect is not None else Table.identifyCSVdialect(csv_str))
		for row in csv_reader:
			no_of_cols: int = len(row)  # (number of columns)
			if columns == []:
				columns = [[] for i in range(0, no_of_cols)]  # (initialize)
			for col_index in range(0, no_of_cols):
				columns[col_index].append(row[col_index])

		result = Table(surroundingText="", headerRow=[],\
			columns=columns)  # surroundingText is not applicable to CSV files
		result.parse_header_row()  # set headerRow!=[] if possible
		return result

	@classmethod
	def parseXLSX(cls, xlsxPath: str) -> Table:
		# Use openpyxl to parse Microsoft Excel files,
		# cf. https://www.geeksforgeeks.org/
		#   working-with-excel-spreadsheets-in-python/

		import openpyxl
		wb_obj = openpyxl.load_workbook(xlsxPath)
		sheet_obj = wb_obj.active

		# # Example from www.geeksforgeeks.org :
		# cell_obj = sheet_obj.cell(row = 1, column = 1)
		# print(cell_obj.value)

		# # Works but does not consider a possible header row:
		# columns = [list(map(lambda cell_obj: str(cell_obj.value), column))\
		# 	for column in sheet_obj.iter_cols()]

		rows = [list(map(lambda cell_obj: str(cell_obj.value), row))\
			for row in sheet_obj.iter_rows()]

		#If Table.parseCSV() took an iterator instead, it would look like this:
		#return Table.parseCSV(csv_lines=(",".join(row) + "\n" for row in rows))
		csv_str = "\n".join([",".join(row) for row in rows])
		return Table.parseCSV(csv_str)

	@classmethod
	def parseJSON(cls, json_str: str, onlyRelational=False,\
		onlyWithHeader=True, useAdditionalHeuristics=False) -> Optional[Table]: # ToDo: change to onlyRelational=True after testing!
		"""
		Parses a .JSON file of the format that's used in the
		WDC Web Table Corpus (http://webdatacommons.org/webtables/2015/
		downloadInstructions.html):

		{"relation":[[..., ...],[..., ...]],
		 "pageTitle":"...",
		 "title":"...",
		 "url":"https://...",
		 "hasHeader":true,
		 "headerPosition":"MIXED",
		 "tableType":"RELATION",
		 "tableNum":6,
		 "s3Link":"common-crawl/crawl-data/...",
		 "recordEndOffset":867273895,
		 "recordOffset":867263717,
		 "tableOrientation":"HORIZONTAL",
		 "textBeforeTable":"...",
		 "textAfterTable":"...",
		 "hasKeyColumn":true,
		 "keyColumnIndex":0,
		 "headerRowIndex":0}

		This method returns None for invalid JSON inputs
		(i.e. not of the above format), for non-relational tables
		(if onlyRelational=True) and for tables without a header
		(if onlyWithHeader=True)!
		"""
		try:
			j = json.loads(json_str)
			
			if onlyRelational and j["tableType"] != "RELATION":
				# e.g. "tableType":"ENTITY"
				return None  # skip non-relational tables

			surroundingText: str =\
				j["textBeforeTable"] + " " + j["textAfterTable"]
			headerRow: List[str] = None
			columns: List[List[str]] = None

			# For the header information, rely on the information given
			#   (i.e. do no own heuristics):
			if j["hasHeader"]:
				if j["headerPosition"] == "FIRST_ROW":  # (most common case)
					headerRow = [col[0] for col in j["relation"]]
					columns = [col[1:] for col in j["relation"]] # strip header
				elif j["headerPosition"] == "FIRST_COLUMN":
					# Tranpose the table because for us, the header is always
					#   in the first row:
					headerRow = j["relation"][0]  # 1st column = header
					columns = transpose(j["relation"][1:]).tolist()
				elif j["headerPosition"] == "MIXED":
					return None  # skipping such unsure/non-relational? tables
				else:
					print("[PARSE ERROR] Unknown value for 'headerPosition'" +\
						f""" in JSON: '{j["headerPosition"]}'""",\
						file=sys.stderr)
					return None
			else:  # "hasHeader":false => "headerPosition":"NONE"
				if onlyWithHeader and not useAdditionalHeuristics:
					# Corpus says that this table has no header, we shall
					#   not use additional heuristcs and we shall only
					#   return tables with header => return None:
					return None
				elif not onlyWithHeader and not useAdditionalHeuristics:
					# Corpus says that this table has no header, we **are**
					#   allowed to return tables without a header but we are
					#   **not** allowed to use additional heuristics
					#   => return the table without header
					#      as it is in the corpus:
					headerRow = []
					# We still have to find out which way to orient the columns
					#   though:
					columns = None  # ToDo(!)
				elif useAdditionalHeuristics:
					# We **are** allowed to use additional heuristics:
					# Looking at some examples shows that when
					#   "hasHeader":false, there **is** usually a header
					#   in the first column...
					return None  # ToDo(!)

			return Table(surroundingText=surroundingText, headerRow=headerRow,\
				columns=columns)
		except BaseException as e:
			# (most likely a KeyError when JSON is in invalid format)
			if DEBUG:
				print(f"[DEBUG] Error parsing JSON: {e}", file=sys.stderr)
			return None

	@classmethod
	def parseTAR(cls, tarPath: str, csv_dialect: Dialect = None)\
		-> Iterator[Table]:
		# cf. https://docs.python.org/3/library/tarfile.html
		tar = tarfile.open(tarPath)
		for tarinfo in tar:
			# Skip directories and hidden files in the TAR archive:
			if tarinfo.isfile() and tarinfo.name[:1] != ".":
				if os.path.splitext(tarinfo.name)[1] == ".json":
					yield Table.parseJSON(\
						json_str=tar.extractfile(tarinfo).read())
				elif os.path.splitext(tarinfo.name)[1] == ".csv":
					yield Table.parseCSV(\
						csv_str=tar.extractfile(tarinfo).read(),\
						dialect=csv_dialect)
				elif os.path.splitext(tarinfo.name)[1] in [".xlsx", ".xls"]:
					# Because parseXLSX() expects a path, we have to
					#   temporarily extract the .xlsx file to the file system:
					table: Table = None
					with tempfile.NamedTemporaryFile() as temp_path:
						# Extract the .xlsx file to a temporary location:
						tar.extract(tarinfo, path=temp_path)
						# Parse that temporary .xlsx file:
						table = Table.parseXLSX(xlsxPath=temp_path)
					yield table
				# All other file types in the TAR archive are ignored.


	@classmethod
	def parseFolder(cls, folderPath: str, recursive=True,\
		csv_dialect: Dialect = None) -> Iterator[Table]:
		# Sorting is important such that the order is predictable to the user:
		for folder_item in sorted(os.listdir(folderPath)):
			folder_item = os.path.join(folderPath, folder_item)
			if os.path.isfile(folder_item):
				file_name, file_extension = os.path.splitext(folder_item)
				if file_extension == ".csv":
					with open(folder_item, 'r', newline='') as csv_file:
						# (newline='' is required by the CSV library)
						yield Table.parseCSV(csv_str=csv_file.read(),\
							dialect=csv_dialect)
				elif file_extension in [".xlsx", ".xls"]:
					yield Table.parseXLSX(xlsxPath=folder_item)
				elif file_extension == ".json":
					with open(folder_item, 'r') as json_file: 
						yield Table.parseJSON(json_str=json_file.read())
				elif file_extension == ".tar":
					for table in Table.parseTAR(tarPath=folder_item):
						yield table
				# Skip files with any other filetype/extension.
			elif recursive:
				for table in Table.parseFolder(folderPath=folder_item,\
					recursive=True):
					yield table
			# When the item is a directory and recursive=False, skip it.

	@classmethod
	def parseCorpus(cls, corpusPath: str, recursive=True,\
		yieldNones=False, csv_dialect: Dialect = None) -> Iterator[Table]:
		if os.path.isfile(corpusPath):
			file_name, file_extension = os.path.splitext(corpusPath)
			if file_extension == ".tar":
				return filter(lambda table: yieldNones or table is not None,\
					Table.parseTAR(tarPath=corpusPath, csv_dialect=csv_dialect))
			else:
				sys.exit("Error: --corpus supplied either has to be a "+\
					" directory or a .TAR file.")
		else:
			return filter(lambda table: yieldNones or table is not None,\
				Table.parseFolder(folderPath=corpusPath, recursive=recursive,\
					csv_dialect=csv_dialect))


# !!!!! ToDo: delete this and create a default_corpus.tar instead !!!!!
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
			"""2BIG & little's1034 W Belmont Ave |
			At N Kenmore Ave Order From This Restaurant""",\
			"""3Brown Bag Seafood Co.340 E Randolph St |
			Btwn N Columbus & N Lake Shore Dr""",\
			"""4Captain Hook's Fish & Chicken8550 S Cottage Grove Ave |
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
			"Don't Say You Love Me"],\
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
    	'entityTypes', # Narratives = "Knowing what to look for"
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

	parser.add_argument('--prefer-textual-surroundings',
		action='store_true',
		help="""Use textual surroundings only, unless this approach yields no
		results whatsoever, then use the other ones.""")

	parser.add_argument('--prefer-attr-names',
		action='store_true',
		help="""Use attribute/column names only, unless this approach yields no
		results whatsoever, then use the other ones.""")

	parser.add_argument('--prefer-attr-extensions',
		action='store_true',
		help="""Use attribute extensions only, unless this approach yields no
		results whatsoever, then use the other ones.""")

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
    	You may use the 'default_corpus.tar' default corpus for testing.
    	Note that all tables smaller than 3x3 are rigorously filtered out.
    	Folders are parsed in alphabetical order.
    	Excel files instead of CSV files are supported too when the
    	`openpyxl` Python module is installed:
    	`pip install openpyxl` or
    	`python3 -m pip install openpyxl`""",
    	metavar='PATH')

	parser.add_argument('--corpus-non-recursive',
		action='store_true',
		help="""When a folder is specified for the --corpus parameter, do NOT
		look into its subfolders recursively.""")

	parser.add_argument('--csv-delimiter',
    	type=str,
    	default='',
    	help="""
    	Specify the delimiter character (e.g. ',' or ';') that's used by the
    	CSV files in the corpus.
    	By default, it is automatically recognized for each CSV file
    	individually. So specify this only when all CSV files in the corpus
    	have a common format!
    	""",
    	metavar='CSV_DELIMITER')

	parser.add_argument('--csv-quotechar',
    	type=str,
    	default='',
    	help="""
    	Specify the quotechar character (e.g. '"') that's used by the
    	CSV files in the corpus.
    	By default, it is automatically recognized for each CSV file
    	individually. So specify this only when all CSV files in the corpus
    	have a common format! 
    	""",
    	metavar='CSV_QUOTECHAR')

	parser.add_argument('--ordered',
		action='store_true',
		help="""When this flag is set, the tables in the output are sorted by
		how well they score. Beware that lazy output is lost which means that
		this flag should not be used together with a very big corpus!""")

	parser.add_argument('--bing',
		action='store_true',
		help="""
		Use the Bing web search and Wikidata for inferring the semantics of
		attribute extensions instead of just Wikidata.
		For this to work, the BING_SEARCH_V7_SUBSCRIPTION_KEY and
		BING_SEARCH_V7_ENDPOINT variables need to be set. You can find
		their values on portal.azure.com
		""")

	parser.add_argument('--webisadb',
		action='store_true',
		help="""
		Use the WebIsA Database from webdatacommons.org/isadb and Wikidata for
		inferring the semantics of attribute extensions instead of just
		Wikidata (cf. the --bing flag which contradicts this flag).
		For this to work, the corresponding MongoDB has to be running
		on localhost.
		""")

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
	group.add_argument('--sbert', action='store_true',
		help="""
		Use SBERT for word similarity of column/attribute names.
		This is currently slower than using the Jaccard index.
		For this to work you need to run `pip install -U sentence-transformers`
		or `python3 -m pip install -U sentence-transformers` first!
		""")

	# Narratives = "Taking Advantage of the Knowledge in the Narrative":

	parser.add_argument('--co-occurring-keywords',
    	type=str,
    	default='',
    	help="""
    	List other words occurring in the narrative. The results are then
    	limited to those tables where at least one of these words occurs in
    	either the surrounding text of the table or inside the table.
    	""",
    	nargs='*',
    	metavar='KEYWORD')

	parser.add_argument('--co-occurring-keywords-all',
		action='store_true',
		help="""
		Set this flag to require all(!) keywords specified with the 
		--co-occurring-keywords parameter to occur in the surrounding text
		of or inside each table.
		(By default, one keyword occuring is regarded as being sufficient.)
		""")

	parser.add_argument('--attribute-cond',
    	type=str,
    	default='',
    	help="""
    	List one or multiple attribute conditions of the form
    	"[attribute name] [<=,>=,<,>,==,!=,in,not in]
    	 [value, value range or value list]", e.g.
        "horsepower >= 500" or
        "year in range(1980,2000)" or
        "firstName not in ['Alex', 'Alexander']"
    	When supplied, the results are limited to those tables where
    	(a) a column name could be matched to each specified attribute name
    	   (--jaccard or --sbert is used, depending on parameter)
    	and
    	(b) all(!) values in the extension of that column fulfill
    	    the specified condition.
    	Note that (a) and (b) are combined, i.e. columns where all values
    	fulfill the condition in (b) are considered to be more likely to match
    	the attribute in (a).
    	Use the --attribute-cond-strictness parameter
    	to specify the strictness of
    	this condition check as a value between 0.0 (no check at all)
    	and 1.0 (100-percent strict).
    	""",
    	nargs='*',
    	metavar='CONDITION')

	parser.add_argument('--attribute-cond-strictness',
    	type=float,
    	default=1.0,
    	help="""
    	Only meaningful in combination with the --attribute-cond parameter.
    	A value between 0.0 (least strict) and 1.0 (most strict, default).
    	""",
    	metavar='STRICTNESS')

	args = parser.parse_args()

	corpus: str = args.corpus
	stats: bool = args.stats
	entityTypes: List[str] = args.entityTypes

	# <preparation>
	print("[PREPARING] Mapping DBpedia classes to wikidata...")
	dbpediaClassesMappedToWikidata =\
		get_dbpedia_classes_mapped_to_wikidata()
	print("[PREPARING] Mapping DBpedia properties to SBERT vectors...")
	dbpediaPropertiesMappedToSBERTvector =\
		get_dbpedia_properties_mapped_to_SBERT_vector()
	print("[PREPARING] Done.")
	# </preparation>

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
		# -> after entering "finish", the statistics
		#    (MRR, Top-k coverage etc. !!!!! for various weightings !!!!!)
		#    are printed and the user is asked whether they want to export
		#    their annotations (Y/n)
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
