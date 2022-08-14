import argparse
from typing import Dict, List, Tuple, Iterator
from collections import defaultdict

def remove_prefix(s: str, prefix: str) -> str:
	len_prefix = len(prefix)
	if s[:len_prefix] == prefix:
		return s[len_prefix:]
	else:
		return s

def long_list_to_short_str(lst: List[float]) -> str:
	if len(lst) <= 7:
		return str(lst)
	else:
		return\
	f"[{lst[0]}, {lst[1]}, ..., {lst[len(lst)//2]}, ..., {lst[-2]}, {lst[-1]}]"

def merge(sorted_list_1: List[float], sorted_list_2: List[float])\
	-> Iterator[Tuple[float, int, int]]:
	"""
	Merges two sorted lists.
	The resulting iterator contains no duplicates, i.e. each value only once.
	"""
	len_sorted_list_1 = len(sorted_list_1)
	len_sorted_list_2 = len(sorted_list_2)

	index1: int = 0
	index2: int = 0
	x: float = float('nan')
	while index1 < len_sorted_list_1 or index2 < len_sorted_list_2:
		if index1 == len_sorted_list_1:
			x = sorted_list_2[index2]
		elif index2 == len_sorted_list_2:
			x = sorted_list_1[index1]
		else:
			x = min(sorted_list_1[index1], sorted_list_2[index2])
		
		while index1 < len_sorted_list_1 and sorted_list_1[index1] == x:
			index1 += 1
		while index2 < len_sorted_list_2 and sorted_list_2[index2] == x:
			index2 += 1
		
		yield x, index1, index2

def ks(sorted_bag: List[float], unsorted_bag: List[float]) -> float:
	"""
	Computes the KS similarity between two given bags of numerical values,
	one already sorted bag and one unsorted bag, efficiently.

	Attention:
	Throws a `ZeroDivisionError` when either of the given bags/lists
	is empty!
	"""

	unsorted_bag.sort()

	one_over_len_sorted_bag: float = 1.0/len(sorted_bag)
	one_over_len_unsorted_bag: float = 1.0/len(unsorted_bag)

	max_difference: float = 0.0

	for x, index1, index2 in merge(sorted_bag, unsorted_bag):
		max_difference = max(max_difference,\
			abs(index1 * one_over_len_sorted_bag -\
				index2 * one_over_len_unsorted_bag))

	return max_difference

def main():
	parser = argparse.ArgumentParser(
		description="""Takes the extension of a numeric column as input
		and tries to match it to a DBpedia property and corresponding class.""")

	parser.add_argument('--types',
    	type=str,
    	default='',
    	help="""Path (or URL) to a .ttl (turtle) file of
    	DBpedia resources mapped to their types (22-rdf-syntax-ns#type).
    	Download an unzip
downloads.dbpedia.org/2016-04/core-i18n/en/instance_types_en.ttl.bz2
    	for example.""",
    	metavar='TTL_PATH',
    	required=False)
	"""
	   523040066 Oct  7  2016 instance_types_dbtax_dbo_en.ttl
	  1170280591 Oct  7  2016 instance_types_dbtax_ext_en.ttl
	   756372528 Jun 16  2016 instance_types_en.ttl
	   531673855 Oct  7  2016 instance_types_lhd_dbo_en.ttl
	   536730187 Oct  7  2016 instance_types_lhd_ext_en.ttl
	   354246575 Oct  7  2016 instance_types_sdtyped_dbo_en.ttl
	  4565067400 Jun 16  2016 instance_types_transitive_en.ttl
	  5131897930 Nov 11  2016 instance_types_transitive_wkd_uris_en.ttl
	   850228848 Nov 11  2016 instance_types_wkd_uris_en.ttl

	DBTax = Unsupervised Learning for DBpedia Taxonomy
	(see https://github.com/dbpedia/DBTax)

	==> /data/dbpedia/data/instance_types_dbtax_dbo_en.ttl <==
	<http://dbpedia.org/resource/0-0-1-3>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://dbpedia.org/ontology/Drug> .

	==> /data/dbpedia/data/instance_types_dbtax_ext_en.ttl <==
	# started 2016-10-07T07:31:43Z
	<http://dbpedia.org/resource/0.0.0.0>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://dbpedia.org/dbtax/Protocol> .

	==> /data/dbpedia/data/instance_types_en.ttl <==
	<http://dbpedia.org/resource/Achilles>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://www.w3.org/2002/07/owl#Thing> .

	==> /data/dbpedia/data/instance_types_lhd_dbo_en.ttl <==
	<http://dbpedia.org/resource/I_Could_Use_Another_You>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://dbpedia.org/ontology/Single> .

	==> /data/dbpedia/data/instance_types_lhd_ext_en.ttl <==
	<http://dbpedia.org/resource/Electoral_district_of_Elizabeth_
	    (South_Australia)>
	<http://purl.org/linguistics/gold/hypernym>
	<http://dbpedia.org/resource/District> .

	==> /data/dbpedia/data/instance_types_sdtyped_dbo_en.ttl <==
	<http://dbpedia.org/resource/Needles_in_the_Cosmic_Haystack>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://dbpedia.org/ontology/Album> .

	==> /data/dbpedia/data/instance_types_transitive_en.ttl <==
	<http://dbpedia.org/resource/Actrius>
	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	<http://schema.org/Movie> .

	==> /data/dbpedia/data/instance_types_transitive_wkd_uris_en.ttl <==
	# <http://dbpedia.org/resource/001_-_Launch_Week>
	  <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	  <http://dbpedia.org/ontology/MusicalWork> <BAD URI: null> .

	==> /data/dbpedia/data/instance_types_wkd_uris_en.ttl <==
	# <http://dbpedia.org/resource/000_Emergency>
	  <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	  <http://www.w3.org/2002/07/owl#Thing> <BAD URI: null> .
	"""

	parser.add_argument('--properties',
    	type=str,
    	default='',
    	help="""Path (or URL) to a .ttl (turtle) file of
    	DBpedia resources mapped to their properties and values.
    	Download an unzip
downloads.dbpedia.org/2016-04/core-i18n/en/infobox_properties_mapped_en.ttl.bz2
    	for example.""",
    	metavar='TTL_PATH',
    	required=False)

	parser.add_argument('-k',
        type=int,
        default=100,
        help="""The number of (DBpedia type, DBpedia property) pairs to output.
        Default value: 100""",
        metavar='K')

	parser.add_argument(
    	'bag',
    	type=float,
    	help="""A bag of numerical values.""",
    	nargs='*',
    	metavar='NUMBER')

	parser.add_argument('--csv-file',
    	type=str,
    	default='',
    	help="""Path to a CSV file. The n-th column specified with the
    	--csv-column argument will be used as input to this script.
    	It has to be a numerical column containing integer or float values!""",
    	metavar='CSV_FILE_PATH',
    	required=False)

	parser.add_argument('--csv-separator',
    	type=str,
    	default='\t',
    	help="""The separator symbol used in the CSV file specified by the
    	--csv-file argument. (Default: TAB)""",
    	metavar='CSV_SEPARATOR',
    	required=False)

	parser.add_argument('--csv-column',
    	type=int,
    	default=0,
    	help="""Which column to use as input in the CSV file given by
    	the --csv-file argument. The first column has index 0.
    	(Default: 0)""",
    	metavar='CSV_COLUMN',
    	required=False)

	parser.add_argument('--compare-with',
    	type=str,
    	help="""
    	Optional parameter: do not just output the k lowest KS scores but also
    	the KS scores regarding these given DBpedia properties or regarding all
    	properties of these given DBpedia types.
        Syntax:
        "type:property", "type:", ":property" (may be arbitrarily combined!)
        Examples: "Place:2006Population", "Place:", ":2006Population"
    	""",
    	nargs='*',
    	metavar='COMPARE_WITH',
    	required=False)

	parser.add_argument('--output',
    	type=str,
    	default='',
    	help="""
    	When this parameter is set, the data parsed and combined from the two
    	.ttl files given in the --types and --properties arguments is also
    	exported to the specified file in TSV (tab-separated values) format.
        That file can then be used later in the --input argument to speed
        things up by saving the parsing of two big .ttl files.
        It is highly recommended to generate the TSV file using the Rust
        version of this script!
    	""",
    	metavar='OUTPUT_FILE_PATH',
    	required=False)

	parser.add_argument('--input',
    	type=str,
    	default='',
    	help="""
    	Specify the TSV file previously generated using the --output parameter
    	(highly recommended to do that with the Rust version of this script).
        When --input is set, the --types and --properties parameters are not
        needed anymore.
    	""",
    	metavar='INPUT_FILE_PATH',
    	required=False)

	args = parser.parse_args()

	# Maps each DBpedia resource to its DBpedia type:
	dbpedia_resource_to_type: Dict[str, str] = {}

	# Maps each pair of a DBpedia type and numeric DBpedia property
	#   to the list of values taken by all DBpedia resources that are an
	#   instance of that type:
	dbpedia_type_and_property_to_extension\
		: Dict[Tuple[str, str], List[float]] = defaultdict(list)

	print("")

	if args.input != "":
		print("[4/6] Populating dictionary with parsed --input TSV file...")

		with open(args.input) as input_tsv:
			for line in input_tsv:
				[dbp_type, dbp_property, extension] = line.split("\t")
				dbpedia_type_and_property_to_extension\
					[(dbp_type, dbp_property)] = eval(extension)
				# e.g.: eval("[1.0, 2.0, 3.0]") == [1.0, 2.0, 3.0]

	elif args.types != "" and args.properties != "":
		from rdflib import Graph  # python3 -m pip install rdflib

		print("[1/6] Parsing --types .ttl file...")

		# Parse the .ttl file passed as --types:
		types_graph = Graph()
		types_graph.parse(args.types, format='turtle')

		print("[2/6] Parsing --properties .ttl file...")

		# Parse the .ttl file passed as --properties:
		properties_graph = Graph()
		properties_graph.parse(args.properties, format='turtle')

		print("[3/6] Populating dictionary with parsed --types .ttl file...")

		# Iterate through the (subject, predicate, object) triples as in
		#   https://rdflib.readthedocs.io/en/stable/gettingstarted.html
		#   and populate dbpedia_resource_to_type:
		for _resource, _rdf_syntax_ns_type, _type in types_graph:
			if not "22-rdf-syntax-ns#type" in _rdf_syntax_ns_type:
				continue

			_resource = remove_prefix(_resource, "http://dbpedia.org/resource/")

			_type = remove_prefix(_type, "http://dbpedia.org/ontology/")

			if "/" in _type:
				continue  # skip Things: (http://)www.w3.org/2002/07/owl#Thing

			dbpedia_resource_to_type[_resource] = _type

			#print(f"{_resource}, {_rdf_syntax_ns_type}, {_type}")

		print(f"[INFO] {len(dbpedia_resource_to_type)} DBpedia resources")

		print("[4/6] Populating dictionary with parsed --properties .ttl file...")

		# Iterate through the (subject, predicate, object) triples as in
		#   https://rdflib.readthedocs.io/en/stable/gettingstarted.html
		#   and populate dbpedia_type_and_property_to_extension:
		for _resource, _property, _value in properties_graph:
			try:
				_value = float(_value)  # ToDo: possibly more advanced parsing

				_resource = remove_prefix(_resource, "http://dbpedia.org/resource/")

				_property = remove_prefix(_property, "http://dbpedia.org/property/")

				_type = dbpedia_resource_to_type[_resource]

				dbpedia_type_and_property_to_extension[(_type, _property)]\
					.append(_value)

				#print(f"{_resource}, {_property}, {_value}")
			except (ValueError, KeyError):
				# (a) ValueError: could not convert string to float, or
				#     -> i.e. property is not numeric
				# (b) KeyError in dbpedia_resource_to_type
				#     -> i.e. type for the given ressource is unknown
				continue
	else:
		print("[ERROR] Please supply either the --input argument or, " +\
			"initially, the --types and --properties arguments! It is " +\
			"highly recommended to do the latter with the Rust version " +\
			"of this script!")
		exit()

	print(f"[INFO] {len(dbpedia_type_and_property_to_extension)} " +\
		"(DBpedia type, numeric DBpedia property) pairs")

	if args.output != "":
		print("[INFO] Writing to --output file...")
		with open(args.output, "w") as file:
			for dbpedia_type_and_property, extension\
				in dbpedia_type_and_property_to_extension.items():
				file.write(f"{dbpedia_type_and_property[0]}\t" +\
					f"{dbpedia_type_and_property[1]}\t{extension}\n")
		print("[INFO] Finished writing to --output file.")

	# The input bag to compare against all DBpedia numerical bags:
	bag: List[float] = []
	if args.csv_file == "":
		bag = args.bag
	else:
		with open(args.csv_file, "r") as f:
			for line in f.readlines():
				if line[:1] == "#" or line.strip() == "":
					continue  # skip comment lines and empty lines
				try:
					bag.append(float(line.split(\
						args.csv_separator)[args.csv_column].strip()))
				except ValueError:
					continue  # skip non-numerical entries in the column
	print("[INFO] Unsorted input bag = " + long_list_to_short_str(bag))
	bag.sort()

	print("[5/6] Computing KS scores...")

	# Maps each pair of a DBpedia type and numeric DBpedia property
	#   to the metric returned by the KS (Kolmogorov–Smirnov) test
	#   on the list of values taken by all DBpedia resources that are an
	#   instance of that type and the input list of numeric values:
	dbpedia_type_and_property_to_ks_test: Dict[Tuple[str, str], float] =\
		{ key : ks(bag, lst)\
		for key, lst in dbpedia_type_and_property_to_extension.items()}

	print("[6/6] Sorting results by KS score...")

	dbpedia_type_and_property_to_ks_test_sorted\
		: List[Tuple[Tuple[str, str], float]] =\
        sorted(dbpedia_type_and_property_to_ks_test.items(),\
            key=lambda tuple: tuple[1],\
            reverse=False)  # smaller KS values == more similar

	print("")
	print("KS Score - DBpedia type - DBpedia property - Matched list")
	print("")
	for i in range(0, min(args.k,\
		len(dbpedia_type_and_property_to_ks_test_sorted[:args.k]))):
		el = dbpedia_type_and_property_to_ks_test_sorted[i]
		dbpedia_type = el[0][0]
		dbpedia_property = el[0][1]
		ks_test_score = el[1]
		matched_list =\
			dbpedia_type_and_property_to_extension[\
			(dbpedia_type, dbpedia_property)]

		print(f"{ks_test_score} - {dbpedia_type} - " +\
			f"{dbpedia_property} - {long_list_to_short_str(matched_list)}")

	if args.compare_with is not None and args.compare_with != []:
		print("")
		print("===== Additional comparisons as specified by the user: =====")
		for compare_with in args.compare_with:
			if compare_with[:1] == ":":  # e.g. ":2006Population"
				dbpedia_property_name = compare_with[1:]  # strip prefix ":"

				for ((t,p), kst) in dbpedia_type_and_property_to_ks_test_sorted:
					if p == dbpedia_property_name:
						matched_list =\
							dbpedia_type_and_property_to_extension[(t, p)]
						print(f"{kst} - {t} - {p} - " +\
							f"{long_list_to_short_str(matched_list)}")
			elif compare_with[-1:] == ":":  # e.g. "Place:"
				dbpedia_type_name = compare_with[:-1]  # strip suffix ":"

				for ((t,p), kst) in dbpedia_type_and_property_to_ks_test_sorted:
					if t == dbpedia_type_name:
						matched_list =\
							dbpedia_type_and_property_to_extension[(t, p)]
						print(f"{kst} - {t} - {p} - " +\
							f"{long_list_to_short_str(matched_list)}")
			elif ":" in compare_with: # e.g. "Place:2006Population"
				[dbpedia_type_name, dbpedia_property_name] =\
					compare_with.split(":")

				for ((t,p), kst) in dbpedia_type_and_property_to_ks_test_sorted:
					if t == dbpedia_type_name and p == dbpedia_property_name:
						matched_list =\
							dbpedia_type_and_property_to_extension[(t, p)]
						print(f"{kst} - {t} - {p} - " +\
							f"{long_list_to_short_str(matched_list)}")
			else:
				print("[ERROR] Invalid value supplied to --compare-with: " +\
					f" '{compare_with}' contains no ':'")

if __name__ == "__main__":
	main()
