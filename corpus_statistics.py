import argparse
import statistics
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
		default=0,
		help="""
		The minimum size a table from the input corpus must have in order to
		be considered. Default: 0
		""",
		metavar='MIN_TABLE_SIZE')

	parser.add_argument('--debug',
		action='store_true',
		help='Print debug info prints.')

	args = parser.parse_args()

	# The total number of tables in the corpus:
	total_number_of_tables: int = 0

	# The number of columns for each table in the corpus:
	number_of_colums_per_table: List[int] = []

	# Count how many tables contain purely numerical / purely textual data
	#   and how many contain a mix of both numerical and textual data:
	number_of_purely_numerical_tables: int = 0
	number_of_purely_textual_tables: int = 0
	number_of_mixed_numerical_and_textual_tables: int = 0

	for table_ in Table.parseCorpus(args.corpus,\
		file_extensions=FileExtensions(), onlyRelationalJSON=\
		args.relational_json_tables_only,\
		min_table_size=args.min_table_size, DEBUG=args.debug):

		if total_number_of_tables == args.stop_after_n_tables:
			break  # Stop after N tables.

		total_number_of_tables += 1

		number_of_cols: int = len(table_.columns)
		number_of_colums_per_table.append(number_of_cols)

		number_of_numerical_columns: int = 0
		number_of_textual_columns: int = 0

		for column in table_.columns:
			first_non_empty_column_value: str = ""
			for column_value in column:
				if column_value.strip() != "":
					first_non_empty_column_value = column_value.strip()
					# => The call of strip() is actually redundant here, as
					#    float(" 3.14 ") == 3.14 also works; it's just here
					#    for clarity.
					break

			# When still first_non_empty_column_value == "",
			#  this column contains only empty cells.
			# An empty column is neither numerical nor textual, so skip it:
			if first_non_empty_column_value == "":
				continue

			try:
				value: float =\
					float(first_non_empty_column_value.replace(',', ''))
				number_of_numerical_columns += 1
			except ValueError:
				number_of_textual_columns += 1

		if number_of_numerical_columns > 0 and number_of_textual_columns > 0:
			number_of_mixed_numerical_and_textual_tables += 1
		elif number_of_numerical_columns > 0:
			number_of_purely_numerical_tables += 1
		elif number_of_textual_columns > 0:
			number_of_purely_textual_tables += 1
			#print(f"Debug: purely textual table: {table_.file_name}")
		else:
			print(f"[INFO] Table {table_.file_name} " +\
				"has zero non-empty columns!")

	number_of_colums_average: float =\
		statistics.mean(number_of_colums_per_table)
	number_of_colums_stdev: float =\
		statistics.stdev(number_of_colums_per_table)

	#print(f"Debug: {number_of_colums_per_table}")

	print("===== Corpus statistics: =====")
	print(f"Total number of tables: {total_number_of_tables}")
	print("\t=> Number of purely numerical tables: " +\
		f"{number_of_purely_numerical_tables} " +\
		f"({100*(number_of_purely_numerical_tables/total_number_of_tables)}%)")
	print("\t=> Number of purely textual tables: " +\
		f"{number_of_purely_textual_tables} " +\
		f"({100*(number_of_purely_textual_tables/total_number_of_tables)}%)")
	print("\t=> Number of mixed (numerical and textual) tables: " +\
		f"{number_of_mixed_numerical_and_textual_tables} " +\
		f"({100*(number_of_mixed_numerical_and_textual_tables/total_number_of_tables)}%)")
	print(f"Number of columns - average: {number_of_colums_average}")
	print(f"Number of columns - standard deviation: {number_of_colums_stdev}")
	
	big_N: int = 30  # should be a 2-digit number, otherwise increase "{i:3d}" below

	for i in range(0, big_N+1):
		tables_with_i_columns: int =\
			len([n for n in number_of_colums_per_table if n == i])
		print(f"Tables with {i:3d} columns: " +\
			f"{tables_with_i_columns} " +\
			f"({100*(tables_with_i_columns/total_number_of_tables)}%)")

	tables_with_more_than_N_columns: int =\
			len([n for n in number_of_colums_per_table if n > big_N])
	print(f"Tables with >{big_N} columns: " +\
			f"{tables_with_more_than_N_columns} " +\
			f"({100*(tables_with_more_than_N_columns/total_number_of_tables)}%)")

if __name__ == "__main__":
	main()
