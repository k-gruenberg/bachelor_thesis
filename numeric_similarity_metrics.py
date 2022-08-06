"""
Subsection "Examining the Distributions of Numeric Columns"
The metrics here stem from Neumaier et al. and Pham et al. (both ISWC 2016)
"""

from typing import List
from math import sqrt
from statistics import mean, stdev
import argparse

def numeric_Jaccard_similarity(a: List[float], b: List[float]) -> float:
	return (min(max(a), max(b)) - max(min(a), min(b))) / \
		   (max(max(a), max(b)) - min(min(a), min(b)))

def numeric_Jaccard_similarity_quartile(a: List[float], b: List[float]) -> float:
	a.sort()
	b.sort()
	a = a[int(0.25*len(a)):int(0.75*len(a))]
	b = b[int(0.25*len(b)):int(0.75*len(b))]
	return numeric_Jaccard_similarity(a, b)

def euclidean_distance(vector_1: List[float], vector_2: List[float]) -> float:
	return sqrt(sum(
			map(
				lambda tuple: (tuple[0] - tuple[1])**2,
				zip(vector_1, vector_2)
			)
		   ))

def euclidean_distance_feature_vector_1(a: List[float], b: List[float]) -> float:
	vector_1 = [min(a), max(a), mean(a), stdev(a)]
	vector_2 = [min(b), max(b), mean(b), stdev(b)]
	return euclidean_distance(vector_1, vector_2)

def euclidean_distance_feature_vector_2(a: List[float], b: List[float]) -> float:
	a.sort()
	b.sort()
	vector_1 = [a[int(0.05*len(a))], a[int(0.95*len(a))], mean(a), stdev(a)]
	vector_2 = [b[int(0.05*len(b))], b[int(0.95*len(b))], mean(b), stdev(b)]
	return euclidean_distance(vector_1, vector_2)

def kolmogorov_smirnov_test(a: List[float], b: List[float]) -> float:
	return max(abs(cumulative_distribution_function(a, x) -\
		cumulative_distribution_function(b, x)) for x in a + b)

def cumulative_distribution_function(a: List[float], x: float) -> float:
	return len([a_ for a_ in a if a_ <= x]) / \
		   len(a)

def main():
	parser = argparse.ArgumentParser(
		description="""Outputs multiple similarity metrics
		for two given bags of numerical values -a and -b.""")

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

	args = parser.parse_args()

	a: List[float] = args.a
	b: List[float] = args.b

	print("")

	try:
		print("Numeric Jaccard similarity: " +\
				str(numeric_Jaccard_similarity(a, b)))
	except:
		print("Numeric Jaccard similarity: ERROR")

	try:
		print("Numeric Jaccard similarity (1st to 3rd quartile): " +\
				str(numeric_Jaccard_similarity_quartile(a, b)))
	except:
		print("Numeric Jaccard similarity (1st to 3rd quartile): ERROR")

	try:
		print("Euclidean distance feature vector #1: " +\
				str(euclidean_distance_feature_vector_1(a, b)))
	except:
		print("Euclidean distance feature vector #1: ERROR")

	try:
		print("Euclidean distance feature vector #2: " +\
				str(euclidean_distance_feature_vector_2(a, b)))
	except:
		print("Euclidean distance feature vector #2: ERROR")

	try:
		print("KS test: " +\
				str(kolmogorov_smirnov_test(a, b)))
	except:
		print("KS test: ERROR")

	print("")

if __name__ == "__main__":
	main()
