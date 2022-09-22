from __future__ import annotations
from typing import List, Tuple, Dict
import argparse
from collections import defaultdict

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

	most_common_column_headings: Dict[str, int] =\
		defaultdict(int)
	most_common_co_occurring_keywords: Dict[str, int] =\
		defaultdict(int)
	most_common_co_occurring_keywords_textual_surr_only: Dict[str, int] =\
		defaultdict(int)
	most_common_co_occurring_keywords_inside_table_only: Dict[str, int] =\
		defaultdict(int)

	for table, classif_result, wikidata_item\
		in tables_with_classif_result_and_correct_entity_type:
		if any(entityType == wikidata_item.entity_id\
			for entityType in args.entityTypes):

			# Update the most common column headings & co-occurring keywords:
			for column_heading in table.headerRow:
				most_common_column_headings[column_heading] += 1
			for word in table.surroundingText.split():
				most_common_co_occurring_keywords[word] += 1
				most_common_co_occurring_keywords_textual_surr_only[word] += 1
			for column in table.columns:
				for cell in column:
					for word in cell.split():
						most_common_co_occurring_keywords[word] += 1
						most_common_co_occurring_keywords_inside_table_only\
							[word] += 1

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

	print("Most common column headings:")
	print(f"{sorted(most_common_column_headings.items(), key=lambda tuple: tuple[1], reverse=True)[:10]}")
	print("")
	print("Most common co-occurring keywords:")
	print(f"{sorted(most_common_co_occurring_keywords.items(), key=lambda tuple: tuple[1], reverse=True)[:10]}")
	print("")
	print("Most common co-occurring keywords (textual surr. only):")
	print(f"{sorted(most_common_co_occurring_keywords_textual_surr_only.items(), key=lambda tuple: tuple[1], reverse=True)[:10]}")
	print("")
	print("Most common co-occurring keywords (inside table only):")
	print(f"{sorted(most_common_co_occurring_keywords_inside_table_only.items(), key=lambda tuple: tuple[1], reverse=True)[:10]}")
	print("")

if __name__ == "__main__":
	main()
