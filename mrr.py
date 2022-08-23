"""
A tiny helper tool for computing the MRR (mean reciprocal rank).
"""

import argparse

def main():
	parser = argparse.ArgumentParser(
		description="""
		A tiny helper tool for computing the MRR (mean reciprocal rank).
		""")

	parser.add_argument(
    	'ranks',
    	type=int,
    	help="""The list of ranks to compute the MRR for.""",
    	nargs='*',
    	metavar='RANK')

	args = parser.parse_args()

	print((1/len(args.ranks)) * sum(1/rank for rank in args.ranks))

if __name__ == "__main__":
	main()
