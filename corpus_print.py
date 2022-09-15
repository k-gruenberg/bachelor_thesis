import argparse
from typing import List

from Table import Table
from FileExtensions import FileExtensions

def main():
	parser = argparse.ArgumentParser(
		description="""
		An additional tool that ships with NETT, printing some interesting
		statistics about the tables in a given corpus.
		""")

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

	parser.add_argument('--stop-after-n-tables',
		type=int,
		default=-1,
		help="""
		Stop after having gone through (at most) N tables in the corpus.
		By default, this is set to -1 which means that it is deactivated.
		When activated, the minimum value is 2 because otherwise the
		standard deviation cannot be computed.""",
		metavar='N')

	parser.add_argument('--relational-json-tables-only',
		action='store_true',
		help="""
		Only consider .json Tables with "tableType" set to "RELATION".
		Note that this may also filter out relational tables falsely classified
		as non-relational by the (WDC) corpus.
		""")

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

	parser.add_argument('--debug',
		action='store_true',
		help='Print debug info prints.')

	args = parser.parse_args()

	counter: int = 0

	for table_ in Table.parseCorpus(args.corpus,\
		file_extensions=FileExtensions(), onlyRelationalJSON=\
		args.relational_json_tables_only,\
		min_table_size=args.min_table_size, DEBUG=args.debug):

		if counter == args.stop_after_n_tables:
			break  # Stop after N tables.

		counter += 1

		print(f"===== ===== ===== Table no. {counter}: ===== ===== =====")
		print(table_.pretty_print())
		print("")
		print("")
		print("")

if __name__ == "__main__":
	main()
