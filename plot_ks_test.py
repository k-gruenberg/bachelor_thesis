import matplotlib.pyplot as plt
import numpy
import argparse
from math import floor, ceil
from numeric_similarity_metrics import *

def main():
	parser = argparse.ArgumentParser(
		description="""Plots the KS test for the
		two given bags of numerical values -a and -b.""")

	parser.add_argument('-a',
    	type=float,
    	help="""The first bag of numerical values.""",
    	nargs='*',
    	metavar='A',
    	required=True)

	parser.add_argument('-b',
    	type=float,
    	help="""The second bag of numerical values.""",
    	nargs='*',
    	metavar='B',
    	required=True)

	parser.add_argument('--step',
		action='store_true',
		help="""Plot as step functions.""")

	args = parser.parse_args()

	a: List[float] = args.a
	b: List[float] = args.b

	if args.step:
		# https://stackoverflow.com/questions/8921296/
		#   how-do-i-plot-a-step-function-with-matplotlib-in-python

		values = [x for x in range(min(floor(min(a)), floor(min(b))) - 1,
			max(ceil(max(a)), ceil(max(b))) + 2)]

		plt.step(values,
			[cumulative_distribution_function(a, x) for x in values],
			'r')
		plt.step(values,
			[cumulative_distribution_function(b, x) for x in values],
			'b')
		plt.show()
	else:
		xpoints = numpy.array(a)
		ypoints = numpy.array(\
			[cumulative_distribution_function(a, x) for x in a])

		plt.plot(xpoints, ypoints, 'r')

		xpoints = numpy.array(b)
		ypoints = numpy.array(\
			[cumulative_distribution_function(b, x) for x in b])

		plt.plot(xpoints, ypoints, 'b')

		plt.show()

if __name__ == "__main__":
	main()
