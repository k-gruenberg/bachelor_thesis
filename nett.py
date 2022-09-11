"""
NETT = Narrative Entity Type(s) to Tables

This program takes as input:
* a corpus of relational tables, either in CSV (or Excel)
  or in a specific JSON format, the one used by the WDC Web Table Corpus
  (the files are allowed to be inside one or multiple .tar archives);
  => you may use the small 'test_corpus' in this repository for testing
  => note that all tables smaller than 3x3 are rigorously filtered out;
     this can be changed using the --min-table-size argument
* optionally: a list of one or more entity types occuring in the narrative that
    is to be grounded (ideally as Wikidata ID's or DBpedia class names,
    otherwise as literal strings then being mapped to Wikidata ID's)
    => you may also supply ids/names of entities instead of entity types,
       in that case they are simply resolved to the entity type they're an
       instance of and the output tables restricted to those containing a
       string equal to that entity's name (more specifially: the name of the
       entity is added to the --co-occurring-keywords)!
* various settings as parameters, see --help, also for more details
  on the 4 different modes of NETT!
"""

from __future__ import annotations
from typing import List, Dict, Any, Iterator, Set
import json  # https://docs.python.org/3/library/json.html
import argparse
import re
import os
import sys
import csv  # https://docs.python.org/3/library/csv.html
import tarfile  # https://docs.python.org/3/library/tarfile.html
import tempfile  # https://docs.python.org/3/library/tempfile.html
import math
from datetime import datetime

from numpy import transpose

from WikidataItem import WikidataItem
from Table import Table
from ClassificationResult import ClassificationResult
from FileExtensions import FileExtensions

# Import the fundamental approaches
#     #1 "Using Textual Surroundings"
#     #2 "Using Attribute Names"
#     #3 "Using Attribute Extensions"
# from the respective Python files:
from filter_nouns_with_heuristics import filter_nouns_with_heuristics_as_dict
from attr_names_to_ontology_class import attr_names_to_ontology_class
from attr_extension_to_ontology_class import attr_extension_to_ontology_class
from attr_extension_to_ontology_class_web_search import\
	attr_extension_to_ontology_class_web_search_list_onto_as_dict

from nett_map_dbpedia_classes_to_wikidata import\
	get_dbpedia_classes_mapped_to_wikidata
from nett_map_dbpedia_properties_to_sbert_vectors import\
	prepare_dbpedia_properties_mapped_to_SBERT_vector


def clear_terminal():
	os.system('cls' if os.name == 'nt' else 'clear')


def print_as_two_columns(text: str, spacing: int = 4) -> str:
	"""
	Halves the number of lines in a multiline string by printing it in two
	columns. Returns a printable string (i.e. performs no printing itself).

	Example:
	>>> print(print_as_two_columns("111\n222\n333\n444\n555"))
	111    444
	222    555
	333    

	>>>
	"""
	lines: List[str] = text.splitlines()
	no_of_lines: int = len(lines)

	# For an odd number of lines, the left column shall be longer than
	#   the right one:
	left_column: List[str] = lines[:math.ceil(no_of_lines / 2)]
	right_column: List[str] = lines[math.ceil(no_of_lines / 2):]

	left_column_width: int = max(len(row) for row in left_column)
	#right_column_width: int = max(len(row) for row in right_column)
	# => not necessary to know

	two_column_result: str = ""

	for row_no in range(0, len(left_column)):
		two_column_result +=\
		left_column[row_no] +\
		" " * (left_column_width-len(left_column[row_no])) +\
		" " * spacing +\
		(right_column[row_no] if row_no < len(right_column) else "") +\
		"\n"

	return two_column_result


def annotations_to_json(\
	annotations: List[Tuple[Table, ClassificationResult, WikidataItem]])\
	-> str:
	"""
	Export the user-made annotations in --stats mode as JSON.
	"""

	# Doesn't work: return json.dumps(annotations, default=vars)

	json_dumpable_annotations: List[Tuple[dict, dict, dict]] =\
		[(vars(table),\
		  {key_string: {key_wikidata_item.entity_id: value_float\
		  				for key_wikidata_item, value_float
		  				in value_dict.items()}
		  	for key_string, value_dict\
		  	in vars(classification_result).items()},\
		  vars(wikidata_item))\
		 for table, classification_result, wikidata_item in annotations]

	return json.dumps(json_dumpable_annotations)


def json_to_annotations(json_str: str)\
	-> List[Tuple[Table, ClassificationResult, WikidataItem]]:
	"""
	Import the user-made annotations in JSON format again,
	exported using the annotations_to_json() function.
	"""
	parsed_annotations_file: List[Tuple[dict, dict, dict]] =\
		json.loads(json_str)
	# Turn the JSON dictionaries into Python classes again:
	tables_with_classif_result_and_correct_entity_type\
		= [(Table(surroundingText=t["surroundingText"],\
				headerRow=t["headerRow"],\
				columns=t["columns"],
				file_name=t["file_name"]),\
			ClassificationResult(resUsingTextualSurroundings=\
				{WikidataItem(k): v\
				 for k, v in cr["resUsingTextualSurroundings"].items()},\
				resUsingAttrNames=\
				{WikidataItem(k): v\
				 for k, v in cr["resUsingAttrNames"].items()},\
				resUsingAttrExtensions=\
				{WikidataItem(k): v\
				 for k, v in cr["resUsingAttrExtensions"].items()}),\
			WikidataItem(entity_id=wi["entity_id"],\
				label=wi["label"],\
				description=wi["description"],\
				properties=wi["properties"]))\
			for (t, cr, wi) in parsed_annotations_file]
	return tables_with_classif_result_and_correct_entity_type


def main():
	parser = argparse.ArgumentParser(
		description="""NETT - Narrative Entity Type(s) to Tables.
		NETT can be run in 4 modes:
		(1) --stats, no ENTITY_TYPE(s) supplied => statistics for given corpus
		(2) --stats, ENTITY_TYPE(s) supplied => statistics for given corpus,
		with focus on the supplied entity types (specifying additional
		narrative knowledge is possible)
		(3) no ENTITY_TYPE(s) supplied => classify all tables in given corpus
		(and possibly use narrative knowledge, although this makes much more
		sense in mode (4).)
		(4) ENTITY_TYPE(s) supplied => main productive mode: search corpus
        for tables containing tuples of the given entity type(s)
        (and possibly use narrative knowledge)!!
		""")
	# ToDo: list a few example calls in this description!!

	parser.add_argument(
    	'entityTypes', # Narratives = "Knowing what to look for"
    	type=str,
    	help="""A list of entity types (the entity types to look for).
    	Ideally they're Wikidata ID's of the form 'Q000000'.
    	Alternatively they're names of DBpedia classes which are then
    	mapped to Wikidata ID's using a pre-programmed mapping table.
    	When they are neither of the form 'Q000000' nor the name of a DBpedia
    	class, Wikidata is searched with them as a search string and the user
    	asked which of the search results is the one they meant.
    	When no entity types are supplied at all, a ranked list of entity types
    	is returned for every table in the corpus instead (mode (3))
    	(assuming that the --stats flag isn't supplied).""",
    	nargs='*',
    	metavar='ENTITY_TYPE')

	parser.add_argument('--corpus',
    	type=str,
    	default='',
    	help="""Path to a folder containing tables as CSV/JSON/TAR files.
    	Or path to a single TAR file containing tables as CSV/JSON files.
    	You may use 'test_corpus' for testing
    	(only contains a handful of tables!).
    	Note that all tables smaller than 3x3 are rigorously filtered out.
    	Folders are parsed in alphabetical order.
    	Excel files instead of CSV files are supported too when the
    	`openpyxl` Python module is installed:
    	`pip install openpyxl` or
    	`python3 -m pip install openpyxl`""",
    	metavar='CORPUS_PATH',
    	required=True)

	parser.add_argument('--corpus-non-recursive',
		action='store_true',
		help="""When a folder is specified for the --corpus parameter, do NOT
		look into its subfolders recursively.""")

	parser.add_argument('--stats',
		action='store_true',
		help="""Ask the user to classify each table in the corpus and return
		statistics in the end. When entity types are supplied as well,
		only tables are shown to the user where NETT believes they *might*
		be of one of these entity types. The statictics in the end are then
		specific to these entity types.""")

	parser.add_argument('-k',
    	type=int,
    	default=1,
    	help="""Only return tables for which the entity type searched for was
    	in the top-k results. By default, k=1 which means that only tables are
    	returned for which the entity type searched for was the best guess.
    	See also: --stats-max-k""",
    	metavar='K')

	parser.add_argument('--stats-max-k',
    	type=int,
    	default=5,
    	help="""This K is relevant when using the --stats flag only.
    	It essentially defines for how many values of k (1,2,3,...,K)
    	the statistics shall be computed and printed.
    	Default value: 5""",
    	metavar='K')

	parser.add_argument('--threshold',
    	type=float,
    	default=0.0,
    	help="""Only return tables for which the entity type searched for got
    	a score of at least this threshold (floating-point number).
    	This makes sense particularly when used together with the --normalize
    	flag. When --normalize is set and all weights are kept at their default
    	value of 1.0, then this value shall be somewhere between 0.0 and 3.0.
    	This is a filter that is set in addition to the -k filter!
    	By default, this threshold is set to 0.0, i.e. it has no effect.""",
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
		results whatsoever, then use the other ones.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	parser.add_argument('--prefer-attr-names',
		action='store_true',
		help="""Use attribute/column names only, unless this approach yields no
		results whatsoever, then use the other ones.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	parser.add_argument('--prefer-attr-extensions',
		action='store_true',
		help="""Use attribute extensions only, unless this approach yields no
		results whatsoever, then use the other ones.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	parser.add_argument('--require-textual-surroundings',
		action='store_true',
		help="""Skip tables without textual surroundings entirely.
		This has the effect of only considering JSON files in the corpus.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	parser.add_argument('--require-attr-names',
		action='store_true',
		help="""Skip tables without attribute names entirely.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	parser.add_argument('--require-attr-extensions',
		action='store_true',
		help="""Skip tables without an identifying/unique column entirely.
		THIS FEATURE IS NOT IMPLEMENTED!""")

	# (ToDo: implement --prefer-... and --require-... parameters)

	parser.add_argument('--normalize',
		action='store_true',
		help="""Whether to normalize the result of each of the 3
    	approaches into the [0,1] range""")

	parser.add_argument('--textual-surroundings-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the textual surroundings approach. Default: 1.0',
    	metavar='WEIGHTING')

	parser.add_argument('--attr-names-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the attribute names approach. Default: 1.0',
    	metavar='WEIGHTING')

	parser.add_argument('--attr-extensions-weight',
    	type=float,
    	default=1.0,
    	help='How to weight the attribute extensions approach. Default: 1.0',
    	metavar='WEIGHTING')

	# (Advanced) ToDo: if all weights are set to 0.0 try out ("learn") which
	#   weights lead to the best results!

	parser.add_argument('--csv-delimiter',  # ToDo: csv_dialect
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

	parser.add_argument('--csv-quotechar',  # ToDo: csv_dialect
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
		this flag should not be used together with a very big corpus!
		This flag only has an effect when in modes (3) and (4), i.e. when
		--stats is *not* set. It makes the most sense in mode (4) however.""")

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
		THIS FEATURE IS NOT IMPLEMENTED!
		""")

	parser.add_argument('--verbose', '-v',
		action='store_true',
		help='Print verbose info prints.')

	parser.add_argument('--debug',
		action='store_true',
		help='Print debug info prints.')

	# cf. https://stackoverflow.com/questions/7869345/
	#     how-to-make-python-argparse-mutually-exclusive-
	#     group-arguments-without-prefix:
	group = parser.add_mutually_exclusive_group(required=True)
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
    	help="""
    	List other words occurring in the narrative. The results are then
    	limited to those tables where at least one of these words occurs in
    	either the surrounding text of the table or inside the table.
    	This will have the side benefit of speeding up the search for tables
    	as tables without any of those keywords can be thrown out immediately,
    	without the need to classify them.
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

	parser.add_argument('--co-occurring-keywords-case-sensitive',
		action='store_true',
		help="Activate case-sensitivity for --co-occurring-keywords.")

	parser.add_argument('--attribute-cond',
    	type=str,
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

	parser.add_argument('--stop-after-n-tables',
    	type=int,
    	default=-1,
    	help="""
    	Stop after having gone through (at most) N tables in the corpus.
    	By default, this is set to -1 which means that it is deactivated.
    	When activated, this only has an effect in modes (3) and (4),
    	i.e. when the --stats flag is not specified.""",
    	metavar='N')

	parser.add_argument('--file-extension-csv',
    	type=str,
    	help="""
    	The extension(s) by which to recognize CSV files.
    	Default: '.csv'
    	""",
    	nargs='*',
    	metavar='EXTENSION_CSV')

	parser.add_argument('--file-extension-xlsx',
    	type=str,
    	help="""
    	The extension(s) by which to recognize Excel files.
    	Default: '.xlsx' and '.xls'
    	""",
    	nargs='*',
    	metavar='EXTENSION_XLSX')

	parser.add_argument('--file-extension-json',
    	type=str,
    	help="""
    	The extension(s) by which to recognize JSON files.
    	Default: '.json'
    	""",
    	nargs='*',
    	metavar='EXTENSION_JSON')

	parser.add_argument('--file-extension-tar',
    	type=str,
    	help="""
    	The extension(s) by which to recognize TAR archives.
    	Default: '.tar'
    	""",
    	nargs='*',
    	metavar='EXTENSION_TAR')

	parser.add_argument('--min-table-size',
    	type=int,
    	default=3,
    	help="""
    	The minimum size a table from the input corpus must have in order to
    	be considered. 3 by default, i.e. all tables smaller than 3x3 are
    	rigorously filtered out (header included).
    	The smallest dimension is considered, meaning that a 2x10 table will
    	also be filtered out!
    	Setting this value to 1 essentially deactivates this filter.
    	""",
    	metavar='MIN_TABLE_SIZE')

	parser.add_argument('--relational-json-tables-only',
		action='store_true',
		help="""
		Only consider .json Tables with "tableType" set to "RELATION".
		Note that this may also filter out relational tables falsely classified
		as non-relational by the (WDC) corpus.
		""")

	parser.add_argument('--annotations-file',
    	type=str,
    	default='',
    	help="""
    	Import your manual annotations again.
    	When you previously exported your annotations as a .json file,
    	you may re-import it using this argument to avoid having to manually
    	reclassify all those tables again.
    	BEWARE: The --jaccard, --sbert, --bing & --webisadb flags had an impact
    	on the exported data but they don't have one on the data imported with
    	this argument! When you exported your data with the --jaccard flag
    	but now want to generate statistics for the --sbert flag for example,
    	you shall **NOT** specify --annotations-file. You instead have to
    	re-annotate your data again!!!
    	""",
    	metavar='ANNOTATIONS_JSON_FILE')

	# ToDo: Virtuoso URL (for speed-up; once Wikidata has been set up @ifis...)
	# ToDo: Database Export & Import (Future Work)

	args = parser.parse_args()

	USER_INPUT_Q00000_REGEX = re.compile(r"Q\d+")
	USER_INPUT_NUMBER_REGEX = re.compile(r"\d+")

	file_extensions: FileExtensions = FileExtensions(\
		CSV_extensions = args.file_extension_csv,\
		XLSX_extensions = args.file_extension_xlsx,\
		JSON_extensions = args.file_extension_json,\
		TAR_extensions = args.file_extension_tar)

	# Parse the ENTITY_TYPE string(s) specified by the user as command line
	#   arguments into a List of WikidataItem's:
	entity_types: List[WikidataItem] = []
	for entityType in args.entityTypes:
		# (1) Parse a string like "Q00000" or "vehicle" to a WikidataItem:
		wikidata_item: WikidataItem = None
		if USER_INPUT_Q00000_REGEX.fullmatch(entityType):  # "Q00000" string:
			wikidata_item = WikidataItem(entityType)
		else:  # A textual string like "vehicle" for example:
			# Search Wikidata with that string and present the user with
			#   the possible WikidataItem canidates, to select the right one:
			wikidata_item_candidates: List[WikidataItem] =\
				WikidataItem.get_items_matching_search_string(entityType)
			print("Which of the following Wikidata items best matches " +\
				f"'{entityType}'?")
			for idx, wi in enumerate(wikidata_item_candidates):
				print(f"({idx}) {wi.entity_id} ({wi.get_label()})")
			print("ENTER NUMBER > ", end="", flush=True)
			user_chosen_index: int = int(input())
			wikidata_item = wikidata_item_candidates[user_chosen_index]
		# (2) When the wikidata_item is an instance of something, use its
		#     class, when its a class in and of itself (i.e. it is a subclass
		#     of another class) use itself, when it's neither, print an error:
		# https://www.wikidata.org/wiki/Property:P31 ("instance of"):
		instance_of_property: List[str] = wikidata_item.get_property("P31")
		# https://www.wikidata.org/wiki/Property:P279 ("subclass of"):
		subclass_of_property: List[str] = wikidata_item.get_property("P279")
		# It's important to check the subclass-of property first, otherwise
		#   Q5 (human) will be mapped to Q55983715 (organisms known by a
		#   particular common name)...:
		if subclass_of_property is not None and subclass_of_property != []:
			# The WikidataItem is a subclass of something:
			entity_types.append(wikidata_item)
		elif instance_of_property is not None and instance_of_property != []:
			# The WikidataItem is an instance of something:
			class_: WikidataItem = WikidataItem(instance_of_property[0])
			print(f"[INFO] {wikidata_item.entity_id} is an instance of " +\
				f"{class_.entity_id} ({class_.get_label()}), NETT will be " +\
				f"looking for tables containing {class_.entity_id} tuples, " +\
				f"restricted to those containing the word '{entityType}' in " +\
				"itself or its surrounding text...")
			entity_types.append(class_)
			# Important: When the user specified an entity instead of an entity
			#            type, don't just map the entity to its entity type
			#            but also add the name of the entity to the
			#            --co-occurring-keywords such that only tables
			#            (probably) containing that entity are returned!
			if args.co_occurring_keywords is None:
				args.co_occurring_keywords = []
			args.co_occurring_keywords.append(entityType)
		else:
			print(f"[ERROR] '{entityType}', mapped to the WikidataItem " +\
				f"{wikidata_item}, is neither an instance nor a subclass " +\
				"of something, skipping it!", file=sys.stderr)

	# <preparation>
	# Prepare SBERT vectors only when SBERT will be used and only if 
	#   preparation is not deactivated:
	if args.sbert:
		print("[PREPARING] Mapping DBpedia properties to SBERT vectors, " +\
			"this may about a minute...")
		prepare_dbpedia_properties_mapped_to_SBERT_vector()
		print("[PREPARING] Done.")
	# </preparation>

	if args.stats:
		# (1) Corpus supplied, statistics requested (evaluation feature):
		#   * Program has to ask user (with the help of pretty_print())
		#     for every table which mapping is correct.
		#   * The user enters enters "1", "2", "3", ...,
		#     "Q000000" (when the correct entity type is not in the list
		#     presented) or "NA" (when the tuples of the table shown cannot be
		#     meaningfully associated with an enity type) for each
		#     table presented, until the whole corpus has been annotated or
		#     until the user stops by entering "finish".
		#   * Then, the statistics (MRR, Top-k coverage; for using
		#     1, 2 or 3 of the three approaches and for various
		#     weightings and preferences of these approaches; also specifically
		#     the "k-recall" for all(!) entity types annotated) are printed
		#     and the user is asked whether they want to export
		#     their annotations (Y/n).
		#   * The --co-occurring-keywords and --attribute-cond parameters
		#     (the "narrative parameters") are ignored in this case as they
		#     make no sense when no entity types are specified.
		#   * The --textual-surroundings-weight, --attr-names-weight,
		#     --attr-extensions-weight and --normalize parameters only
		#     have an effect for the 1st manual annoation part but not for
		#     the 2nd part where the statistics are printed!
		#
		# (2) Corpus and entity types supplied, statistics requested
		#     (evaluation feature):
		#   * Like the case (1) but this time, looking for one (or multiple)
		#     specific entity types.
		#   * Tables for which NETT believes their tuples definitely do not
		#     belong to any of these entity types, are skipped and not
		#     presented to the user at all.
		#   * Tables for which NETT believes their tuples might belong to any
		#     of these entity types, are presented to the user in the same way
		#     as in case (1).
		#   * In the end, statistics are printed (just as in case (1));
		#     beware however that the statistics may not be entirely accurate
		#     when NETT wrongly skipped tables it thought definitely do not
		#     represent any of the entity types searched for.
		#   * Note that it also makes sense to use the --co-occurring-keywords
		#     and --attribute-cond parameters here
		#     (the "narrative parameters").
		#   * The user is shown both tables that match this narrative knowledge
		#     and tables that don't (for a better evaluation afterwards).

		# Tables with classification result and correct entity type specified
		#   by user:
		tables_with_classif_result_and_correct_entity_type:\
			List[Tuple[Table, ClassificationResult, WikidataItem]]\
			= []

		# The user specified a file containing annotations previously made:
		if args.annotations_file != "":
			with open(args.annotations_file, "r") as f:
				tables_with_classif_result_and_correct_entity_type =\
					json_to_annotations(f.read())

		for table_ in Table.parseCorpus(args.corpus,\
			file_extensions=file_extensions, onlyRelationalJSON=\
			args.relational_json_tables_only,\
			min_table_size=args.min_table_size, DEBUG=args.debug):
			# Skip table if it was already annotated (this only happens
			#   when args.annotations_file != ""):
			if args.annotations_file != "" and table_ in [t for (t, cr, wi) in\
				tables_with_classif_result_and_correct_entity_type]:
				continue  # Skip table, it's already annotated.

			# Clear terminal:
			clear_terminal()

			# Print (annotation) progress at the top:
			print("[" +\
				f"{len(tables_with_classif_result_and_correct_entity_type)}"\
				+ " tables annotated so far]")
			print("")

			# Pretty-print table:
			print(table_.pretty_print())
			print("")

			# Print surrounding text associated with table
			#   (limited to 1250 chars; 1500 also possible but it's close!):
			if len(table_.surroundingText) <= 1250:
				print(f"Surrounding text: '{table_.surroundingText}'")
			else:
				print(f"Surrounding text: '{table_.surroundingText[:625]}' " +\
					f"[...] '{table_.surroundingText[-625:]}'")
			print("")

			# Print classification result:
			print("Classification result (please wait...):")
			classification_result_generic: ClassificationResult =\
				table_.classifyGenerically(\
				 useSBERT=args.sbert,\
				 useBing=args.bing,\
				 useWebIsAdb=args.webisadb,\
				 printProgressTo=sys.stdout,\
				 DEBUG=args.debug)
			classification_result: List[Tuple[float, WikidataItem]] =\
				classification_result_generic.classify(\
				 useTextualSurroundings=not args.dont_use_textual_surroundings,\
				 textualSurroundingsWeighting=args.textual_surroundings_weight,\
				 useAttrNames=not args.dont_use_attr_names,\
				 attrNamesWeighting=args.attr_names_weight,\
				 useAttrExtensions=not args.dont_use_attr_extensions,\
				 attrExtensionsWeighting=args.attr_extensions_weight,\
				 normalizeApproaches=args.normalize,\
				 DEBUG=args.debug
				)
			# The maximum number of classification results
			#   to print to the user:
			MAX_NUMBER_OF_RESULTS: int = 40
			classification_result_len: int = min(MAX_NUMBER_OF_RESULTS,\
				len(classification_result))
			classification_result_printable: str = ""
			for i in range(0, classification_result_len):
				score: float = classification_result[i][0]
				wikidata_item: WikidataItem = classification_result[i][1]
				classification_result_printable +=\
					f"({(i+1):2d}) {score:9.4f} {wikidata_item.entity_id} " +\
					f"({wikidata_item.get_label()[:25]}; " +\
					f"{wikidata_item.get_description()[:25]})\n"
			if classification_result_len <= 20:  # list classification results:
				print(classification_result_printable)
			else:  # list classification results in two columns:
				print(print_as_two_columns(classification_result_printable))
			#print("")  # (should not be necessary)

			# Ask user to say which of the entity types is the correct one:
			print("Please enter which of the above entity types is the " +\
				"correct one, as a number ('1', '2', '3', etc.). " +\
				"When multiple entity types match, please enter the smaller " +\
				"number. When none of the entity types match, please enter " +\
				"the correct Wikidata ID using the 'Q00000' syntax. " +\
				"When no entity type is applicable at all, enter 'NA'. " +\
				"Enter 'finish' to stop annotating.")
			user_answer: str = ""
			while user_answer.lower() != "finish"\
				and user_answer.upper() != "NA"\
				and not USER_INPUT_Q00000_REGEX.fullmatch(user_answer)\
				and not USER_INPUT_NUMBER_REGEX.fullmatch(user_answer):
				# Keep asking for input as long as user answer is invalid:
				print("ENTER > ", end="", flush=True)
				user_answer: str = input()

			# User gave a valid answer:
			if user_answer.lower() == "finish":
				break  # exit loop, the user wants to finish.
			elif user_answer.upper() == "NA":
				continue  # skip this invalid (non-relational) table
			elif USER_INPUT_Q00000_REGEX.fullmatch(user_answer):
				user_specified_wikidata_item: WikidataItem =\
					WikidataItem(user_answer)
				tables_with_classif_result_and_correct_entity_type\
					.append((table_,\
						classification_result_generic,\
						user_specified_wikidata_item))
			elif USER_INPUT_NUMBER_REGEX.fullmatch(user_answer):
				user_specified_wikidata_item: WikidataItem =\
					classification_result[int(user_answer)-1][1]
				tables_with_classif_result_and_correct_entity_type\
					.append((table_,\
						classification_result_generic,\
						user_specified_wikidata_item))

		clear_terminal()
		annotations_json_file_path: str =\
			"~/annotations_" + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") +\
			".json"  # e.g. "annotations_01_01_2022_12_00_00.json"
		print("Do you wish to export your annotations to " +\
			f"{annotations_json_file_path}? [Y/n] > ",\
			end="", flush=True)
		user_answer: str = input()
		if user_answer.lower() != "n":
			# Export user annotations as a JSON file:
			with open(os.path.expanduser(annotations_json_file_path), 'x') as f:
				f.write(annotations_to_json(\
					tables_with_classif_result_and_correct_entity_type))

		# Compute statistics and print them:
		clear_terminal()
		if entity_types == []:  # mode (1) (--stats w/o narrative knowledge):
			ClassificationResult.print_statistics(\
				tables_with_classif_result_and_correct_entity_type=\
				tables_with_classif_result_and_correct_entity_type,\
				stats_max_k=args.stats_max_k,\
				DEBUG=args.debug)
		else:  # mode (2) (--stats with narrative knowledge):  # ToDo !!!!!
			print("Looked for tables containing one of the following " +\
				f"entity types: {entity_types}")
			print("...with " + \
				f"{'all' if args.co_occurring_keywords_all else 'one'} of " +\
				"the following co-occurring keywords: " +\
				f"{args.co_occurring_keywords}")
			print(f"...and fulfilling the following attribute conditions " +\
				f"(strictness {args.attribute_cond_strictness}): " +\
				f"{args.attribute_cond}")
			print(f"Out of the {} tables manually annotated, {} were annotated with one of the entity types from {entity_types}")
			print("")

			no_of_correct_rejections: int = None  # ToDo !!!!!
			no_of_incorrect_rejections: int = None  # ToDo !!!!!
			print(f"In total, there were {no_of_correct_rejections} " +\
				f"correct and {no_of_incorrect_rejections} incorrect " +\
				"rejections using the narrative restrictions.")
			print("")

			for k in range(1, args.stats_max_k+1):
				print(f"========== k={k}: ==========")

				recall_without_narratives: float = None  # ToDo !!!!!
				recall_with_narratives: float = None  # ToDo !!!!!
				print(f"Recall for {entity_types}, w/o narrative " +\
					f"conditions: {recall_without_narratives}")
				print(f"Recall for {entity_types}, with narrative " +\
					f"conditions: {recall_with_narratives}")
				print(f"Δ Recall (by using narrative knowledge): " +\
					f"{recall_with_narratives-recall_without_narratives}")
				print("")

				precision_without_narratives: float = None  # ToDo !!!!!
				precision_with_narratives: float = None  # ToDo !!!!!
				print(f"Precision for {entity_types}, w/o narrative " +\
					f"conditions: {precision_without_narratives}")
				print(f"Precision for {entity_types}, with narrative " +\
					f"conditions: {precision_with_narratives}")
				print(f"Δ Precision (by using narrative knowledge): " +\
					f"{precision_with_narratives-precision_without_narratives}")
				print("")
	elif not args.stats:
		# (3) Corpus supplied, entity-type-mappings requested
		#     (evaluation feature, sort of):
		#   * Map all tables of the given corpus to the top-k entity types.
		#   * It might be sensible to change k to a bigger value
		#     than 1 (default).
		#   * For very big corpora, only the first 10,000 annotatable
		#     relational tables are considered. Then, the program terminates.
		#   * The --co-occurring-keywords and --attribute-cond parameters
		#     (the "narrative parameters") may be used but they make much more
		#     sense in mode (4)!
		#
		# (4) Corpus and entity types supplied, tables requested
		#     (the main productive feature!!!):
		#   * Search the corpus for tables whose tuples represent one
		#     of the given entity types, possibly making use of the narrative
		#     knowledge provided with the --co-occurring-keywords and
		#     --attribute-cond parameters (the "narrative parameters").
		#   * Depending on your requirements for precision and recall, you may
		#     want to change the -k parameter to a value other than 1.
		#     With k=1, only tables are retured for which the entity type
		#     searched for was the best match
		#     (i.e. highest possible precision, lowest possible recall).
		#     For bigger k, the recall is higher but the precision lower.

		# Keep a decreasing counter, in case the --stop-after-n-tables argument
		#   is set to a non-negative value:
		decreasing_counter: int = args.stop_after_n_tables

		# This list is only populated when the --ordered flag is set:
		unordered_results: List[Tuple[str, List[Tuple[float, str, str]]]] = []
		# (The 1st tuple item is the file name,
		#  the 2nd one the classification result:
		#  a list of (score, Wikidata ID, Wikidata label) triples.)

		# For each Table in the corpus specified via the --corpus argument...:
		for table_ in Table.parseCorpus(args.corpus, file_extensions=\
			file_extensions, onlyRelationalJSON=\
			args.relational_json_tables_only,\
			min_table_size=args.min_table_size, DEBUG=args.debug):

			# Stop iterating over the corpus after N tables, where N is
			#   specified via the --stop-after-n-tables flag.
			# If N is set to a negative value (-1 by default actually),
			#   the following check will always be false, i.e. we will never
			#   stop iterating before the corpus has been parsed completely:
			if decreasing_counter == 0:
				break
			decreasing_counter -= 1

			if args.debug:
				print(f"[DEBUG] Considering table '{table_.file_name}':")

			# ...check if it satisfies the narrative conditions specified
			#    using the --co-occurring-keywords and --attribute-cond
			#    parameters, when specified, ...:
			# Do the --co-occurring-keywords check first as it should be faster
			#   (only string search, no computation of similarity metrics
			#    needed as with --attribute-cond):
			if args.co_occurring_keywords is not None\
				and args.co_occurring_keywords != []:
				if not table_.has_co_occurring_keywords(\
					keywords=args.co_occurring_keywords,\
					requireAll=args.co_occurring_keywords_all,\
					lookInSurroundingText=True,\
					lookInsideTable=True,\
					caseSensitive=args.co_occurring_keywords_case_sensitive):
					continue  # Skip this table (before even classifying it).
			if args.attribute_cond is not None and args.attribute_cond != []:
				skip_this_table: bool = False
				for attribute_condition in args.attribute_cond:
					if not table_.fulfills_attribute_condition(\
						attribute_cond=attribute_condition,\
						useSBERT=args.sbert,\
						strictness=args.attribute_cond_strictness,\
						DEBUG=args.debug):
						skip_this_table = True  # Skip this table.
						break
				if skip_this_table:
					continue  # Skip this table (before even classifying it).

			# ...classify the Table...:
			classification_result: List[Tuple[float, WikidataItem]] =\
				table_.classify(\
				 useSBERT=args.sbert,\
				 useBing=args.bing,\
				 useWebIsAdb=args.webisadb,\
				 useTextualSurroundings=not args.dont_use_textual_surroundings,\
				 textualSurroundingsWeighting=args.textual_surroundings_weight,\
				 useAttrNames=not args.dont_use_attr_names,\
				 attrNamesWeighting=args.attr_names_weight,\
				 useAttrExtensions=not args.dont_use_attr_extensions,\
				 attrExtensionsWeighting=args.attr_extensions_weight,\
				 normalizeApproaches=args.normalize,\
				 printProgressTo=\
				 	sys.stdout if args.verbose else open(os.devnull,"w"),\
				 DEBUG=args.debug
				)

			# Apply the --k parameter:
			classification_result = classification_result[:args.k]

			# When in mode (4), i.e. when entity_types != [],
			#   skip Tables where none of the top-k entity types returned
			#   by the classification is in the `entity_types` list:
			if entity_types != []:  # mode (4):
				if not any(wi in entity_types\
					for score, wi in classification_result):
					continue  # Skip this table, i.e. print nothing.  

			# ...turn that classification into a human-readable form
			#    and print it (or delay printing when --ordered flag is set):
			classification_result: List[Tuple[float, str, str]] =\
				[(score, wi.entity_id, wi.get_label())\
				 for score, wi in classification_result]
			if not args.ordered:
				print(f"{table_.file_name}: {classification_result}")
			else:
				unordered_results.append(\
					(table_.file_name, classification_result))

		# The --ordered flag was set, which means that no results were printed
		#   yet. Now, we shall return the collected results in descending
		#   order:
		if args.ordered:
			print("[INFO] All results collected. Now sorting them...")
			# First sort...:
			if entity_types == []:  # mode (3):
				# Sort by the score of the best match, in descending order:
				unordered_results.sort(reverse=True,\
					key=lambda tupl: tupl[1][0][0])
			else:  # mode (4):
				# Sort by the score of the best match, in descending order,
				#   but only considering the entity types in entity_types:
				unordered_results.sort(reverse=True,\
					key=lambda tupl: [score\
					for score, wikidata_id, wikidata_label in tupl[1]\
					if WikidataItem(wikidata_id) in entity_types][0])
			# ...then print:
			for table_file_name, classification_result in unordered_results:
				print(f"{table_file_name}: {classification_result}")


if __name__ == "__main__":
	main()
