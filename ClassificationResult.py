from __future__ import annotations
from typing import List, Dict, Any, Iterator, Set

from WikidataItem import WikidataItem
import Table

def combine3(dct1: Dict[WikidataItem, float], weight1: float,\
			dct2: Dict[WikidataItem, float], weight2: float,\
			dct3: Dict[WikidataItem, float], weight3: float)\
			-> List[Tuple[float, WikidataItem]]:
	allWikidataItems = set(dct1.keys())\
						.union(set(dct2.keys()))\
						.union(set(dct3.keys()))
	result: List[Tuple[float, WikidataItem]] =\
		[(weight1 * dct1.get(wi, 0.0) +\
		 weight2 * dct2.get(wi, 0.0) +\
		 weight3 * dct3.get(wi, 0.0),\
		 wi) for wi in allWikidataItems]
	result.sort(key=lambda tuple: tuple[0], reverse=True)
	return result

def normalize(dct: Dict[WikidataItem, float])\
	-> Dict[WikidataItem, float]:
	"""
	Normalizes the values of the input dictionary into the [0.0, 1.0] range.
	"""
	if dct is None:
		return None
	elif dct == {}:
		# Would otherwise raise a 'ValueError: min() arg is an empty sequence':
		return {}
	elif len(dct) == 1:
		# Would otherwise raise a 'ZeroDivisionError: float division by zero'
		#   (since max_value - min_value == 0 when there's only 1 item):
		return {w: 1.0 for w, f in dct.items()}
	else:
		min_value: float = min(dct.values())
		max_value: float = max(dct.values())
		return {w: (f - min_value) / (max_value - min_value)\
				for w, f in dct.items()}

def top_k_coverage(k: int, ranks: List[float]) -> float:
	return len([rank for rank in ranks if rank <= k]) / len(ranks)

def recall_macro_avg(k: int,\
	ranks_per_entity_type: Dict[WikidataItem, List[float]]) -> float:
	return sum(len(rank for rank in ranks if rank <= k) / len(ranks)\
			 for entityType, ranks in ranks_per_entity_type.items())\
			 / len(ranks_per_entity_type)

def index(lst, element) -> float:
	"""
	A generalization of the ["a", "b", "c"].index("b") function
	that returns float('inf') when the element is not found in the list:
	index(["a", "b", "c"], "b") == 1
	index(["a", "b", "c"], "d") == float('inf')
	"""
	return lst.index(element) if element in lst else float('inf')

class ClassificationResult:
	"""
	This is a class particularly useful for generating statistics
	when the user supplied the --stats flag to NETT.
	It allows computing a classification for the same table many times
	using varying parameters, efficiently.

	In the constructor, the classification results of all 3 approaches
	(Using Textual Surroundings, Using Attribute Names
	& Using Attribute Extensions) are given idenpendently of one another.

	Only when calling the classify() method, one has to specify which
	of the 3 approaches to use, whether to normalize the scores and how
	to weight the 3 approaches.
	"""

	def __init__(self,\
		resUsingTextualSurroundings: Dict[WikidataItem, float],\
		resUsingAttrNames: Dict[WikidataItem, float],\
		resUsingAttrExtensions: Dict[WikidataItem, float]\
		):
		self.resUsingTextualSurroundings = resUsingTextualSurroundings
		self.resUsingAttrNames = resUsingAttrNames
		self.resUsingAttrExtensions = resUsingAttrExtensions

	def classify(self,\
				 useTextualSurroundings=True, textualSurroundingsWeighting=1.0,\
				 useAttrNames=True, attrNamesWeighting=1.0,\
				 useAttrExtensions=True, attrExtensionsWeighting=1.0,\
				 normalizeApproaches=False, DEBUG=False)\
				-> List[Tuple[float, WikidataItem]]:

		resultUsingTextualSurroundings: Dict[WikidataItem, float] =\
			self.resUsingTextualSurroundings

		resultUsingAttrNames: Dict[WikidataItem, float] =\
			self.resUsingAttrNames

		resultUsingAttrExtensions: Dict[WikidataItem, float] =\
			self.resUsingAttrExtensions

		if DEBUG:
			print("[DEBUG] Classifying using " +\
				f"{len(resultUsingTextualSurroundings)} results from using " +\
				f"textual surroundings, {len(resultUsingAttrNames)} results " +\
				"from using attribute names and " +\
				f"{len(resultUsingAttrExtensions)} results from using " +\
				"attribute extensions.")

		if normalizeApproaches:
			resultUsingTextualSurroundings =\
				normalize(resultUsingTextualSurroundings)
			resultUsingAttrNames = normalize(resultUsingAttrNames)
			resultUsingAttrExtensions = normalize(resultUsingAttrExtensions)

		combinedResult: List[Tuple[float, WikidataItem]] =\
			combine3(\
			dct1=resultUsingTextualSurroundings\
				if useTextualSurroundings else {},\
			weight1=textualSurroundingsWeighting,\
			dct2=resultUsingAttrNames\
				if useAttrNames else {},\
			weight2=attrNamesWeighting,\
			dct3=resultUsingAttrExtensions\
				if useAttrExtensions else {},\
			weight3=attrExtensionsWeighting,\
		)

		return combinedResult

	@classmethod
	def print_statistics(cls,\
		tables_with_classif_result_and_correct_entity_type:\
		List[Tuple[Table, ClassificationResult,  WikidataItem]],\
		stats_max_k: int = 5) -> None:

		# 3 of 3 approaches, then 2 of 3, then 1 of 3:
		for useTextualSurroundings, useAttrNames, useAttrExtensions in\
			[(True, True, True),\
			 (False, True, True), (True, False, True), (True, True, False),\
			 (True, False, False), (False, True, False), (False, False, True)]:

			ClassificationResult.print_statistics_overall(\
				tables_with_classif_result_and_correct_entity_type,
				stats_max_k=stats_max_k,
				useTextualSurroundings=useTextualSurroundings,
				useAttrNames=useAttrNames,
				useAttrExtensions=useAttrExtensions
			)
			print("")
			ClassificationResult.print_statistics_entity_type_specific(\
				tables_with_classif_result_and_correct_entity_type,
				stats_max_k=stats_max_k,
				useTextualSurroundings=useTextualSurroundings,
				useAttrNames=useAttrNames,
				useAttrExtensions=useAttrExtensions
			)
			print("")
		

	@classmethod
	def print_statistics_overall(cls,\
		tables_with_classif_result_and_correct_entity_type:\
		List[Tuple[Table, ClassificationResult, WikidataItem]],\
		useTextualSurroundings: bool,\
		useAttrNames: bool,\
		useAttrExtensions: bool,\
		textualSurroundingsWeighting=1.0,\
		attrNamesWeighting=1.0,\
		attrExtensionsWeighting=1.0,\
		normalizeApproaches=False,\
		stats_max_k: int = 5,\
		DEBUG=False) -> None:  # ToDo: use new default parameters!!!!!
		"""
		Print statistics on how well (measured in top-k coverage and recall)
		the gives tables are classified, when
		using different values of k (from 1 to stats_max_k, inclusive) and when
		using different weightings of the used approaches.
		Which (subset) of the 3 approaches to use is fixed and specified using
		the `useTextualSurroundings`, `useAttrNames`, `useAttrExtensions`
		parameters!

		By default, all approaches are weighted equally and no normalization
		is performed. Otherwise, supply custom values for the
		`textualSurroundingsWeighting`, `attrNamesWeighting`,
		`attrExtensionsWeighting` and `normalizeApproaches` parameters.
		Beware however that statistics based on various choices of weightings
		are **already** printed anyways!
		=> ToDo: decide on whether to ignore the --weight and --normalize
		         command line arguments or not, i.e. whether to supply
		         non-default parameters to THIS function (currently not)!!!
		"""

		# Precomputations:

		tables_with_classif_fixed_params:\
			List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]]\
			= [(tab,\
				classification_result.classify(\
					useTextualSurroundings=useTextualSurroundings,\
					textualSurroundingsWeighting=textualSurroundingsWeighting,\
				 	useAttrNames=useAttrNames,\
				 	attrNamesWeighting=attrNamesWeighting,\
				 	useAttrExtensions=useAttrExtensions,\
				 	attrExtensionsWeighting=attrExtensionsWeighting,\
				 	normalizeApproaches=normalizeApproaches,\
				 	DEBUG=DEBUG),\
				wikidata_item)\
				for tab, classification_result, wikidata_item\
				in tables_with_classif_result_and_correct_entity_type]

		number_of_tables: int = len(tables_with_classif_fixed_params)

		# The rank of the correct entity type for each classified table,
		#   or infinity when none of the entity types in the list returned
		#   by the classification was correct:
		ranks: List[float] = []  # (floats only to allow for infinity)
		for table, classification, wikid_itm\
			in tables_with_classif_fixed_params:
			ranks.append(index([wi for score, wi in classification], wikid_itm))

		# All the wikidata entity types annotated by the user
		#   as the correct ones:
		all_correct_wikidata_types: Set[WikidataItem] = set(wikidata_item\
			for tab, classification_result, wikidata_item\
			in tables_with_classif_fixed_params)

		# Each entity table mapped to the list of rankings it received
		#   (when it was the correct one!):
		ranks_per_entity_type: Dict[WikidataItem, List[float]] =\
			{wikidata_entity_type:\
				[index([wi for score, wi in classification], wikid_itm)\
				for table, classification, wikid_itm\
				in tables_with_classif_fixed_params\
				if wikid_itm == wikidata_entity_type]\
				for wikidata_entity_type in all_correct_wikidata_types\
			}

		# Compute overall statistics and print them:
		if useTextualSurroundings and useAttrNames and useAttrExtensions:
			print("===== Overall stats (using all 3 approaches): =====")
		elif useAttrNames and useAttrExtensions:
			print("===== Overall stats (using attr. names & ext.): =====")
		elif useTextualSurroundings and useAttrExtensions:
			print("===== Overall stats (using text. surr. & attr. ext.): =====")
		elif useTextualSurroundings and useAttrNames:
			print("===== Overall stats (using text. surr. & attr. names): =====")
		elif useTextualSurroundings:
			print("===== Overall stats (using text. surr. only): =====")
		elif useAttrNames:
			print("===== Overall stats (using attr. names only): =====")
		elif useAttrExtensions:
			print("===== Overall stats (using attr. ext. only): =====")
		else:
			exit("Called print_statistics_overall() with " +\
				"all approaches set to False")
		mrr: float = sum(1/rank for rank in ranks) / len(ranks)
		print(f"MRR: {mrr}")
		print(Table.Table(surroundingText="",\
			headerRow=[\
			"k",\
			"Top-k coverage (%)",\
			"Recall (%), macro-average"\
			],columns=[\
			[str(k)\
			 for k in range(1, stats_max_k+1)],\
			["{:8.4f}".format(100.0 * top_k_coverage(k=k, ranks=ranks))\
			 for k in range(1, stats_max_k+1)],\
			["{:8.4f}".format(100.0 * recall_macro_avg(k=k,\
				ranks_per_entity_type=ranks_per_entity_type))\
			 for k in range(1, stats_max_k+1)]\
			]).pretty_print())

		# At last, print tables showing the effects of varying the
		# weightings (with and without normalization):
		#       For 3 approaches, a 3D table like this:
		#                  w1=0.0 w1=0.1 w1=0.2 ... w1=1.0
		#       k=1 w2=0.0
		#       k=1 w2=0.1      ...either top-k coverage or top-k recall...
		#       k=1 w2=0.2      in "normalized / non-normalized" format...
		#
		#       (w3 always such that w1+w2+w3 == 1.0)
		#
		#       For 2 approaches, a 2D table like this:
		#           w1=0.0 w1=0.1 w1=0.2 ... w1=1.0
		#       k=1 
		#       k=1     ...either top-k coverage or top-k recall...
		#       k=1     in "normalized / non-normalized" format...
		#       ...
		# 
		#       (w2 always such that w1+w2 == 1.0)
		if useTextualSurroundings and useAttrNames and useAttrExtensions:
			print("Top-k coverage for different weightings of the 3 approaches"+\
				" (normalized/non-normalized):")
			print(Table.Table.create3DStatisticalTable(\
				_lambda=lambda w1, k, w2: f"ToDo / ToDo",\
				x_var_name="w1", left_y_var_name="k", right_y_var_name="w2"
				).pretty_print())

			print("Recall, macro-avg. for diff. weightings of the 3 approaches"+\
				" (normalized/non-normalized):")
			# ToDo
		elif useAttrNames and useAttrExtensions:
			print("Top-k coverage for different weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo

			print("Recall, macro-avg. for diff. weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo
		elif useTextualSurroundings and useAttrExtensions:
			print("Top-k coverage for different weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo

			print("Recall, macro-avg. for diff. weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo
		elif useTextualSurroundings and useAttrNames:
			print("Top-k coverage for different weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo

			print("Recall, macro-avg. for diff. weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			# ToDo
		else:
			# For 1 approach, it makes no sense to consider different
			#   weightings, so print/do nothing here:
			pass


	@classmethod
	def print_statistics_entity_type_specific(cls,\
		tables_with_classif_result_and_correct_entity_type:\
		List[Tuple[Table, ClassificationResult,  WikidataItem]],\
		useTextualSurroundings: bool,\
		useAttrNames: bool,\
		useAttrExtensions: bool,\
		stats_max_k: int = 5) -> None:  # ToDo!!!!!
		# Compute entity type-specific statistics and print them:
		print("===== Entity type-specific recalls " +\
			"(using parameters given): =====")
		print(Table.Table(surroundingText="",\
			headerRow=["Entity type"] +\
				[f"k={k}" for k in range(1, stats_max_k+1)],\
			columns=[[enityType for enityType\
			in all_correct_entity_types_annotated]] +\
			[[None] for k in range(0, stats_max_k)]\
			).pretty_print()) # ToDo
