from __future__ import annotations
from typing import List, Tuple
import argparse

from WikidataItem import WikidataItem
from Table import Table
from ClassificationResult import ClassificationResult
from nett import json_to_annotations

def main():
	parser = argparse.ArgumentParser(
		description="""
		A helper tool that retrieves the manual annotations for a given
		list of table file name match strings.
		""")

	parser.add_argument(
    	'tableFileNameMatchStrings',
    	type=str,
    	help="""A list of strings. All tables whose filename contains
    	any of these strings as a substring is considered.""",
    	nargs='*',
    	metavar='TABLE_FILE_NAME_MATCH_STRING')

	parser.add_argument('--annotations-file',
    	type=str,
    	help="""
    	The .json file(s) containing the manual annotations, cf.
    	the same argument of NETT.
    	""",
    	nargs='*',
    	metavar='ANNOTATIONS_JSON_FILE')

	args = parser.parse_args()

	# Tables with classification result and correct entity type specified
	#   by user:
	tables_with_classif_result_and_correct_entity_type:\
		List[Tuple[Table, ClassificationResult, WikidataItem]]\
		= []

	# The user specified a file (or multiple files)
	#   containing annotations previously made:
	if args.annotations_file is not None and args.annotations_file != []:
		for annotations_file in args.annotations_file:
			with open(annotations_file, "r") as f:
				tables_with_classif_result_and_correct_entity_type +=\
					json_to_annotations(f.read())
	else:
		exit("Please specify at least one --annotations-file!")

	print(f"{len(args.tableFileNameMatchStrings)} match strings provided.")
	print(f"{len(args.annotations_file)} annotation files provided.")
	print("")

	# Iterating first through the manual annotations, then through the
	#   match strings:
	"""
	for table, classif_result, wikidata_item\
		in tables_with_classif_result_and_correct_entity_type:
		if any(matchString in table.file_name\
			for matchString in args.tableFileNameMatchStrings):
			# Print table file name & manual annotation (correct WikidataItem):
			print(f"{table.file_name[-80:]}: {wikidata_item}")
	"""

	# Iterating first through the match strings, then through the
	#   manual annnotations:
	for matchString in args.tableFileNameMatchStrings:
		match_found: bool = False
		for table, classif_result, wikidata_item\
			in tables_with_classif_result_and_correct_entity_type:
			if matchString in table.file_name:
				match_found = True
				print(f"{matchString}: {wikidata_item}")
		if not match_found:
			print(f"{matchString}: N/A")

if __name__ == "__main__":
	main()
