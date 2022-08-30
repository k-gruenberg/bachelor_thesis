"""
NETT = Narrative Entity Type(s) to Tables

This program takes as input:
* a corpus of relational tables, either in CSV (or Excel)
  or in a specific JSON format
  (the files are allowed to be inside one or multiple .tar archives);
  when no corpus is specified a small default corpus is being used
  => note that all tables smaller than 3x3 are rigorously filtered out
* optionally: a list of one or more entity types occuring in the narrative that
    is to be grounded (ideally as Wikidata ID's or DBpedia class names,
    otherwise as literal strings then being mapped to Wikidata ID's)
    => you may also supply ids/names of entities instead of entity types,
       in that case they are simply resolved to the entity type they're an
       instance of and the output tables restricted to those containing a
       string equal or similar to that entity's name # ToDo: this feature!
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

from numpy import transpose

from WikidataItem import WikidataItem
from Table import Table
from ClassificationResult import ClassificationResult

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
	initalize_dbpedia_properties_mapped_to_SBERT_vector,\
	get_dbpedia_properties_mapped_to_SBERT_vector

DEBUG = True


def clear_terminal():
	os.system('cls' if os.name == 'nt' else 'clear')


def print_as_two_columns(text: str, spacing: int = 4) -> str:
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


def main():
	parser = argparse.ArgumentParser(
		description="""NETT - Narrative Entity Type(s) to Tables.
		NETT can be run in 4 modes:
		(1) --stats, no ENTITY_TYPE(s) supplied => statistics for given corpus
		(2) --stats, ENTITY_TYPE(s) supplied => statistics for given corpus,
		with focus on the supplied entity types (specifying additional
		narrative knowledge is possible)
		(3) no ENTITY_TYPE(s) supplied => classify all tables in given corpus
		(but max. 10,000 tables)
		(4) ENTITY_TYPE(s) supplied => main productive mode: search corpus
        for tables based on given entity/-ies
        (and possibly narrative knowledge)!!
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
    	returned for which the entity type searched for was the best guess.""",
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
		results whatsoever, then use the other ones.""")

	parser.add_argument('--prefer-attr-names',
		action='store_true',
		help="""Use attribute/column names only, unless this approach yields no
		results whatsoever, then use the other ones.""")

	parser.add_argument('--prefer-attr-extensions',
		action='store_true',
		help="""Use attribute extensions only, unless this approach yields no
		results whatsoever, then use the other ones.""")

	parser.add_argument('--require-textual-surroundings',
		action='store_true',
		help="""Skip tables without textual surroundings entirely.
		This has the effect of only considering JSON files in the corpus.""")

	parser.add_argument('--require-attr-names',
		action='store_true',
		help='Skip tables without attribute names entirely.')

	parser.add_argument('--require-attr-extensions',
		action='store_true',
		help='Skip tables without an identifying/unique column entirely.')

	# ToDo: how to implement --prefer and --require parameters?! -> remove?!

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
		this flag should not be used together with a very big corpus!
		This flag only has an effect when in "productive mode" (4), i.e. when
		entity types are supplied and --stats is *not* set.""")

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

	parser.add_argument('--stop-after-n-tables',
    	type=int,
    	default=10000,
    	help="""Stop after (at most) N tables.
    	This only has an effect in mode (3),
    	i.e. when neither --stats is specified nor any entity types.
    	Default value: 10000""",
    	metavar='N')

	args = parser.parse_args()

	DEBUG = args.debug

	# <preparation>
	if args.sbert:  # Prepare SBERT vectors only when SBERT will be used:
		print("[PREPARING] Mapping DBpedia properties to SBERT vectors...")
		initalize_dbpedia_properties_mapped_to_SBERT_vector()
		print("[PREPARING] Done.")
	# </preparation>

	USER_INPUT_Q00000_REGEX = re.compile(r"Q\d+")
	USER_INPUT_NUMBER_REGEX = re.compile(r"\d+")

	if args.stats and args.entityTypes == []:
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

		tables_with_classif_result_and_correct_entity_type_specified_by_user:\
			List[Tuple[Table, ClassificationResult,  WikidataItem]]\
			= []  # ToDo: shorten name

		for table_ in Table.parseCorpus(args.corpus, DEBUG=args.debug):
			# Clear terminal:
			clear_terminal()

			# Pretty-print table:
			print(table_.pretty_print())
			print("")

			# Print surrounding text associated with table:
			print(f"Surrounding text: '{table_.surroundingText}'")
			print("")

			# Print classification result:
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
			classification_result_len: int = len(classification_result)
			classification_result_printable: str = ""
			for i in range(0, classification_result_len):
				score: float = classification_result[i][0]
				wikidata_item: WikidataItem = classification_result[i][1]
				classification_result_printable +=\
					f"({i+1}) {score:10.4f} {wikidata_item.entity_id} " +\
					f"({wikidata_item.get_label()}; " +\
					f"{wikidata_item.get_description()[:20]})\n"
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
				print("ENTER > ", flush=True)
				user_answer: str = input()

			# User gave a valid answer:
			if user_answer.lower() == "finish":
				break  # exit loop, the user wants to finish.
			elif user_answer.upper() == "NA":
				continue  # skip this invalid (non-relational) table
			elif USER_INPUT_Q00000_REGEX.fullmatch(user_answer):
				user_specified_wikidata_item: WikidataItem =\
					WikidataItem(user_answer)
				tables_with_classif_result_and_correct_entity_type_specified_by_user\
					.append((table_,\
						classification_result_generic,\
						user_specified_wikidata_item))
			elif USER_INPUT_NUMBER_REGEX.fullmatch(user_answer):
				user_specified_wikidata_item: WikidataItem =\
					classification_result[int(user_answer)-1][1]
				tables_with_classif_result_and_correct_entity_type_specified_by_user\
					.append((table_,\
						classification_result_generic,\
						user_specified_wikidata_item))

		# The set of all (correct) entity types occuring in the given corpus:
		all_correct_entity_types_annotated: Set[WikidataItem] =\
			set(correct_entity_type\
				for table, classification_result, correct_entity_type in\
				tables_with_classif_result_and_correct_entity_type_specified_by_user)

		# Compute statistics and print them:
		clear_terminal()
		ClassificationResult.print_statistics(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user=\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,\
			stats_max_k=args.stats_max_k)		
	elif args.stats and args.entityTypes != []:
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
		print("This combination of parameters is not yet implemented.")  # ToDo
		# ToDo: supply args.sbert & args.debug to fulfills_attribute_condition()
	elif not args.stats and args.entityTypes == []:
		# (3) Corpus supplied, entity-type-mappings requested
		#     (evaluation feature, sort of):
		#   * Map all tables of the given corpus to the top-k entity types.
		#   * It might be sensible to change k to a bigger value
		#     than 1 (default).
		#   * For very big corpora, only the first 10,000 annotatable
		#     relational tables are considered. Then, the program terminates.
		#   * The --co-occurring-keywords and --attribute-cond parameters
		#     (the "narrative parameters") are ignored in this case as they
		#     make no sense when no entity types are specified.
		decreasing_counter: int = args.stop_after_n_tables  # default: 10000
		for table_ in Table.parseCorpus(args.corpus, DEBUG=args.debug):
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
			classification_result: List[Tuple[float, str, str]] =\
				list(map(lambda tuple: (\
					tuple[0], tuple[1].entity_id, tuple[1].get_label()),\
					classification_result[:args.k]))
			print(f"{table_.file_name}: {classification_result}")
			decreasing_counter -= 1
			if decreasing_counter == 0:
				break
	elif not args.stats and args.entityTypes != []:
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
		print("This combination of parameters is not yet implemented.")  # ToDo!
		# ToDo: supply args.sbert & args.debug to fulfills_attribute_condition()


if __name__ == "__main__":
	main()
