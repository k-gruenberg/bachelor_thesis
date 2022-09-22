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
		A helper tool that retrieves the tables manually annotated with
		a certain entity type from one or multiple .json files containing
		manual annotations.
		This is similar in principle to NETT, the tables just aren't retrieved
		based on a complex classification mechanism but based on previous
		manual annotations.
		""")

	parser.add_argument(
    	'entityTypes',
    	type=str,
    	help="""A list of entity types (the entity types to look for).
    	They have to be Wikidata ID's of the form 'Q000000'.
    	""",
    	nargs='*',
    	metavar='ENTITY_TYPE')

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

	print(f"{len(args.entityTypes)} entity types provided.")
	print(f"{len(args.annotations_file)} annotation files provided.")
	print("")

	counter: int = 1

	for table, classif_result, wikidata_item\
		in tables_with_classif_result_and_correct_entity_type:
		if any(entityType == wikidata_item.entity_id\
			for entityType in args.entityTypes):
			# Print table file name & manual annotation (correct WikidataItem):
			print("===== ===== ===== " +\
				f"Table #{counter} '{table.file_name[-80:]}'' " +\
				f"(annotated as '{wikidata_item}'): ===== ===== =====")
			# Print table itself:
			print(table.pretty_print())
			print("")
			print("")  # (cf. corpus_print.py)
			print("")
			counter += 1

if __name__ == "__main__":
	main()
