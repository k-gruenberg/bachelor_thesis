from __future__ import annotations
from typing import List, Dict, Any, Iterator, Set
import math

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
	# Sort, first by score (descending) and then by
	#   Wikidata entity ID for equal scores (ascending); this is to ensure
	#   deterministic(!) results (especially deterministic --stats):
	result.sort(key=lambda tuple:\
		(tuple[0], 1.0/float(tuple[1].entity_id[1:])), reverse=True)
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
		if min_value == max_value:
			# Would otherwise raise a 'ZeroDivisionError':
			# When all values are equal, normalize them all to 1.0:
			return {w: 1.0 for w, f in dct.items()}
		return {w: (f - min_value) / (max_value - min_value)\
				for w, f in dct.items()}

def aggregate_subclasses_into_superclasses(\
	combine3_result: List[Tuple[float, WikidataItem]])\
	-> List[Tuple[float, WikidataItem]]:
	return combine3_result  # ToDo

def aggregate_superclasses_into_subclasses(\
	combine3_result: List[Tuple[float, WikidataItem]])\
	-> List[Tuple[float, WikidataItem]]:
	return combine3_result  # ToDo

def top_k_coverage(k: int, ranks: List[float]) -> float:
	"""
	Top-k coverage.
	Returns what fraction of ranks in `ranks` is < k.
	It's important that it's "<" and not "<=" since ranks begin at 0 but
	k begins at 1!
	"""
	return len([rank for rank in ranks if rank < k]) / len(ranks)

def recall_macro_avg(k: int,\
	ranks_per_entity_type: Dict[WikidataItem, List[float]]) -> float:
	"""
	The macro-average computes the recall first for each entity type
	independently and then returns the average over all of those recalls.
	"""
	return sum(len([rank for rank in ranks if rank < k]) / len(ranks)\
			 for entityType, ranks in ranks_per_entity_type.items())\
			 / len(ranks_per_entity_type)

def entity_type_specific_recall(k: int,\
	ranks_per_entity_type: Dict[WikidataItem, List[float]],\
	entity_type: WikidataItem) -> float:
	"""
	This function computes the (k-)recall for one specific entity type.
	With k-recall, we mean the recall when drawing all the top-k results
	and demanding one of them to be the correct one.
	"""
	ranks: List[float] = ranks_per_entity_type[entity_type]
	return len([rank for rank in ranks if rank < k]) / len(ranks)

def index(lst, element) -> float:
	"""
	A generalization of the ["a", "b", "c"].index("b") function
	that returns float('inf') when the element is not found in the list:
	index(["a", "b", "c"], "b") == 1
	index(["a", "b", "c"], "d") == float('inf')
	"""
	return lst.index(element) if element in lst else float('inf')

def entity_type_specific_precision(k: int,\
	ranks_per_entity_type: Dict[WikidataItem, List[float]],\
	tables_with_classif:\
			List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]],\
	entity_type: WikidataItem) -> float:
	"""
	This function computes the (k-)precision for one specific entity type.
	With k-precision, we mean how many of the results are actually of that
	entity type when drawing all results where the entity type is within
	the top-k candidates.
	"""
	# Compute true positives (correct_ranks):
	correct_ranks: List[float] = ranks_per_entity_type[entity_type]

	# Compute false positives (incorrect_ranks):
	incorrect_ranks: List[float] =\
		[index([wi for score, wi in classif], entity_type)\
		for table, classif, correct_wi in tables_with_classif\
		if correct_wi != entity_type]
	# ...computes the rank of `entity_type` everywhere where it is INCORRECT!

	# Apply the k parameter:
	correct_ranks = [rank for rank in correct_ranks if rank < k]
	incorrect_ranks = [rank for rank in incorrect_ranks if rank < k]

	# Compute and return precision; which is defined as:
	#   true positives / (true positives + false positives)
	if len(correct_ranks) + len(incorrect_ranks) == 0:
		return float('nan')
	else:
		return len(correct_ranks) / (len(correct_ranks) + len(incorrect_ranks))

def precision_macro_avg(k: int,\
	ranks_per_entity_type: Dict[WikidataItem, List[float]],\
	tables_with_classif:\
			List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]]\
	) -> float:
	"""
	The macro-average computes the precision first for each entity type
	independently and then returns the average over all of those precisions.
	"""
	entity_type_specific_precisions: List[float] =\
		[entity_type_specific_precision(\
			k=k,\
			ranks_per_entity_type=ranks_per_entity_type,\
			tables_with_classif=tables_with_classif,\
			entity_type=entity_type)\
		for entity_type in ranks_per_entity_type.keys()]
	entity_type_specific_precisions =\
		[precision for precision in entity_type_specific_precisions\
		if not math.isnan(precision)]  # != float('nan') doesn't work!!!
	return sum(entity_type_specific_precisions)\
		/ len(entity_type_specific_precisions)

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
				 normalizeApproaches=False,\
				 aggregateIntoSuperclasses=False,\
				 aggregateIntoSubclasses=False,\
				 DEBUG=False)\
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

		if aggregateIntoSuperclasses and aggregateIntoSubclasses:
			exit("ClassificationResult.classify(): " +\
				"Cannot aggregate both into superclasses and subclasses!")
		elif aggregateIntoSuperclasses:
			combinedResult =\
				aggregate_subclasses_into_superclasses(combinedResult)
		elif aggregateIntoSubclasses:
			combinedResult =\
				aggregate_superclasses_into_subclasses(combinedResult)

		return combinedResult

	@classmethod
	def print_statistics(cls,\
		tables_with_classif_result_and_correct_entity_type:\
		List[Tuple[Table, ClassificationResult,  WikidataItem]],\
		stats_max_k: int = 5, DEBUG=False) -> None:

		print("========== Statistics (based on " +\
			f"{len(tables_with_classif_result_and_correct_entity_type)}" +\
			" manual classifications): ==========")
		print("")

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
				useAttrExtensions=useAttrExtensions,
				DEBUG=DEBUG
			)
			print("")
			ClassificationResult.print_statistics_entity_type_specific(\
				tables_with_classif_result_and_correct_entity_type,
				stats_max_k=stats_max_k,
				useTextualSurroundings=useTextualSurroundings,
				useAttrNames=useAttrNames,
				useAttrExtensions=useAttrExtensions,
				DEBUG=DEBUG
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
		DEBUG=False) -> None:
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
			ranks.append(\
				index([wi for score, wi in classification], wikid_itm))

		# All the wikidata entity types annotated by the user
		#   as the correct ones, i.e. the set of all (correct) entity types
		#   occuring in the given corpus:
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
			print(f"===== Overall stats (using all 3 approaches with " +\
				  f"w1={textualSurroundingsWeighting}, " +\
				  f"w2={attrNamesWeighting}, " +\
				  f"w3={attrExtensionsWeighting}): =====")
		elif useAttrNames and useAttrExtensions:
			print("===== Overall stats (using attr. names " +\
				  f"(w2={attrNamesWeighting}) & "+\
				  f"attr. ext. (w3={attrExtensionsWeighting})): =====")
		elif useTextualSurroundings and useAttrExtensions:
			print("===== Overall stats (using text. surr. " +\
				  f"(w1={textualSurroundingsWeighting}) & " +\
				  f"attr. ext. (w3={attrExtensionsWeighting})): =====")
		elif useTextualSurroundings and useAttrNames:
			print("===== Overall stats (using text. surr. " +\
				  f"(w1={textualSurroundingsWeighting}) & " + \
				  f"attr. names (w2={attrNamesWeighting})): =====")
		elif useTextualSurroundings:
			print("===== Overall stats (using text. surr. only): =====")
		elif useAttrNames:
			print("===== Overall stats (using attr. names only): =====")
		elif useAttrExtensions:
			print("===== Overall stats (using attr. ext. only): =====")
		else:
			exit("Called print_statistics_overall() with " +\
				"all approaches set to False")
		mrr: float = sum(1/(1+rank) for rank in ranks) / len(ranks)
		print(f"MRR: {mrr}")
		print(Table.Table(surroundingText="",\
			headerRow=[\
			"k",\
			"Top-k coverage (%)",\
			"Recall (%), macro-average",\
			"Precision (%), macro-avg."\
			],columns=[\
			[str(k)\
			 for k in range(1, stats_max_k+1)],\
			["{:8.4f}".format(100.0 * top_k_coverage(k=k, ranks=ranks))\
			 for k in range(1, stats_max_k+1)],\
			["{:8.4f}".format(100.0 * recall_macro_avg(k=k,\
				ranks_per_entity_type=ranks_per_entity_type))\
			 for k in range(1, stats_max_k+1)],\
			["{:8.4f}".format(100.0 * precision_macro_avg(k=k,\
				ranks_per_entity_type=ranks_per_entity_type,\
				tables_with_classif=tables_with_classif_fixed_params))\
			 for k in range(1, stats_max_k+1)]\
			]).pretty_print(maxNumberOfTuples=stats_max_k))

		# At last, print tables showing the effects of varying the
		# weightings (with and without normalization):
		#       For 3 approaches, a 3D table like this:
		#                  w1=0.0 w1=0.1 w1=0.2 ... w1=1.0
		#       k=1 w2=0.0
		#       k=1 w2=0.1      ...either top-k coverage or top-k recall...
		#       k=1 w2=0.2      in "normalized / non-normalized" format...
		#
		#       (w3 always such that w1+w2+w3 == 2.0)
		#
		#       For 2 approaches, a 2D table like this:
		#           w1=0.0 w1=0.1 w1=0.2 ... w1=1.0
		#       k=1 
		#       k=1     ...either top-k coverage or top-k recall...
		#       k=1     in "normalized / non-normalized" format...
		#       ...
		# 
		#       (w2 always such that w1+w2 == 1.0)
		def top_k_coverage_w(k: int, normalize: bool, w1: float, w2: float, w3: float = None) -> str:
			"""
			Returns the top-k coverage, for the k and three weightings
			specified, as a 4-character string (e.g. ' 42%').
			The `useTextualSurroundings`, `useAttrNames` and
			`useAttrExtensions` booleans are taken from the outer function.
			"""
			if w3 is None:
				w3 = 1.0-w1-w2

			# Precomputations:

			tables_with_classif_fixed_params:\
				List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]]\
				= [(tab,\
					classification_result.classify(\
						useTextualSurroundings=useTextualSurroundings,\
						textualSurroundingsWeighting=w1,\
					 	useAttrNames=useAttrNames,\
					 	attrNamesWeighting=w2,\
					 	useAttrExtensions=useAttrExtensions,\
					 	attrExtensionsWeighting=w3,\
					 	normalizeApproaches=normalize,\
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
				ranks.append(\
					index([wi for score, wi in classification], wikid_itm))

			return "{:3.0f}%".format(100.0 * top_k_coverage(k=k, ranks=ranks))

		def recall_macro_avg_w(k: int, normalize: bool, w1: float, w2: float, w3: float = None) -> str:
			"""
			Returns the recall (macro-average), for the k and three weightings
			specified, as a 4-character string (e.g. ' 42%').
			The `useTextualSurroundings`, `useAttrNames` and
			`useAttrExtensions` booleans are taken from the outer function.
			"""
			if w3 is None:
				w3 = 1.0-w1-w2

			# Precomputations:

			tables_with_classif_fixed_params:\
				List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]]\
				= [(tab,\
					classification_result.classify(\
						useTextualSurroundings=useTextualSurroundings,\
						textualSurroundingsWeighting=w1,\
					 	useAttrNames=useAttrNames,\
					 	attrNamesWeighting=w2,\
					 	useAttrExtensions=useAttrExtensions,\
					 	attrExtensionsWeighting=w3,\
					 	normalizeApproaches=normalize,\
					 	DEBUG=DEBUG),\
					wikidata_item)\
					for tab, classification_result, wikidata_item\
					in tables_with_classif_result_and_correct_entity_type]

			number_of_tables: int = len(tables_with_classif_fixed_params)

			# All the wikidata entity types annotated by the user
			#   as the correct ones, i.e. the set of all (correct) entity types
			#   occuring in the given corpus:
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

			return "{:3.0f}%".format(100.0 * recall_macro_avg(k=k,\
				ranks_per_entity_type=ranks_per_entity_type))

		def mrr_w_float(normalize: bool, w1: float, w2: float, w3: float = None) -> float:
			"""
			Returns the mean reciprocal rank (MRR), for the three weightings
			specified, as a 4-character string (e.g. '.123').
			The `useTextualSurroundings`, `useAttrNames` and
			`useAttrExtensions` booleans are taken from the outer function.
			"""
			if w3 is None:
				w3 = 1.0-w1-w2

			# Precomputations:

			tables_with_classif_fixed_params:\
				List[Tuple[Table, List[Tuple[float, WikidataItem]], WikidataItem]]\
				= [(tab,\
					classification_result.classify(\
						useTextualSurroundings=useTextualSurroundings,\
						textualSurroundingsWeighting=w1,\
					 	useAttrNames=useAttrNames,\
					 	attrNamesWeighting=w2,\
					 	useAttrExtensions=useAttrExtensions,\
					 	attrExtensionsWeighting=w3,\
					 	normalizeApproaches=normalize,\
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
				ranks.append(\
					index([wi for score, wi in classification], wikid_itm))
			
			mrr: float = sum(1/(1+rank) for rank in ranks) / len(ranks)
			return mrr

		def mrr_w(normalize: bool, w1: float, w2: float, w3: float = None) -> str:
			mrr: float = mrr_w_float(normalize=normalize, w1=w1, w2=w2, w3=w3)
			if mrr >= 0.9995:  # (would otherwise falsely turn into '.000')
				return "1.00"  # length = 4 characters
			else:
				return "{:1.3f}".format(mrr)[1:]  # [1:] turns '0.123' into '.123'

		if useTextualSurroundings and useAttrNames and useAttrExtensions:
			# Use all 3 approaches:
			print("Top-k coverage for different weightings of the 3 approaches"+\
				" (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):")
			print(Table.Table.create3DStatisticalTable(\
				_lambda=lambda w1, k, w2:\
				f"{top_k_coverage_w(k=k, w1=w1, w2=w2, w3=2.0-w1-w2, normalize=True)}"\
				" / " +\
				f"{top_k_coverage_w(k=k, w1=w1, w2=w2, w3=2.0-w1-w2, normalize=False)}",\
				x_var_name="w1", left_y_var_name="k", right_y_var_name="w2",\
				left_y_range=list(range(1, stats_max_k+1))
				).pretty_print(maxNumberOfTuples=100000000))

			print("Recall, macro-avg. for diff. weightings of the 3 approaches"+\
				" (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):")
			print(Table.Table.create3DStatisticalTable(\
				_lambda=lambda w1, k, w2:\
				f"{recall_macro_avg_w(k=k, w1=w1, w2=w2, w3=2.0-w1-w2, normalize=True)}"\
				" / " +\
				f"{recall_macro_avg_w(k=k, w1=w1, w2=w2, w3=2.0-w1-w2, normalize=False)}",\
				x_var_name="w1", left_y_var_name="k", right_y_var_name="w2",\
				left_y_range=list(range(1, stats_max_k+1))
				).pretty_print(maxNumberOfTuples=100000000))

			print("MRR for diff. weightings of the 3 approaches"+\
				" (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):")
			print(Table.Table.create2DStatisticalTable(\
				_lambda=lambda w1, w2:\
				f"{mrr_w(w1=w1, w2=w2, w3=2.0-w1-w2, normalize=True)}"\
				" / " +\
				f"{mrr_w(w1=w1, w2=w2, w3=2.0-w1-w2, normalize=False)}",\
				x_var_name="w1",\
				y_var_name="w2"\
				).pretty_print(maxNumberOfTuples=100000000))

			# Try out the optimal MRR:
			optimal_mrr: float = -1.0
			optimal_w1: float = float('nan')
			optimal_w2: float = float('nan')
			optimal_w3: float = float('nan')
			optimal_normalize: bool = None
			# Try out 2*10*10*10 = 2,000 combinations of weightings and
			#   normalization:
			for normalize in [True, False]:
				for w1 in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
					for w2 in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
						for w3 in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
							mrr: float =\
								mrr_w_float(w1=w1, w2=w2, w3=w3, normalize=normalize)
							if mrr > optimal_mrr:
								optimal_mrr = mrr
								optimal_w1 = w1
								optimal_w2 = w2
								optimal_w3 = w3
								optimal_normalize = normalize
			print(f"The optimal MRR of {optimal_mrr} is achieved for " +\
				f"w1={optimal_w1}, w2={optimal_w2}, w3={optimal_w3}, " +\
				f"normalize={optimal_normalize}!")
		elif (useAttrNames and useAttrExtensions)\
			or (useTextualSurroundings and useAttrExtensions)\
			or (useTextualSurroundings and useAttrNames):
			# Use 2 of the 3 approaches:
			print("Top-k coverage for different weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			print(Table.Table.create2DStatisticalTable(\
				_lambda=lambda w, k:\
				f"{top_k_coverage_w(k=k, w1=(w if useTextualSurroundings else 0.0), w2=(w if not useTextualSurroundings else (1.0-w if useAttrNames else 0.0)), normalize=True)}"\
				" / " +\
				f"{top_k_coverage_w(k=k, w1=(w if useTextualSurroundings else 0.0), w2=(w if not useTextualSurroundings else (1.0-w if useAttrNames else 0.0)), normalize=False)}",\
				x_var_name=("w1" if useTextualSurroundings else "w2"),\
				y_var_name="k",\
				y_range=list(range(1, stats_max_k+1))
				).pretty_print(maxNumberOfTuples=100000000))

			print("Recall, macro-avg. for diff. weightings of the 2 approaches"+\
				" (normalized/non-normalized):")
			print(Table.Table.create2DStatisticalTable(\
				_lambda=lambda w, k:\
				f"{recall_macro_avg_w(k=k, w1=(w if useTextualSurroundings else 0.0), w2=(w if not useTextualSurroundings else (1.0-w if useAttrNames else 0.0)), normalize=True)}"\
				" / " +\
				f"{recall_macro_avg_w(k=k, w1=(w if useTextualSurroundings else 0.0), w2=(w if not useTextualSurroundings else (1.0-w if useAttrNames else 0.0)), normalize=False)}",\
				x_var_name=("w1" if useTextualSurroundings else "w2"),\
				y_var_name="k",\
				y_range=list(range(1, stats_max_k+1))
				).pretty_print(maxNumberOfTuples=100000000))
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
		textualSurroundingsWeighting=1.0,\
		attrNamesWeighting=1.0,\
		attrExtensionsWeighting=1.0,\
		normalizeApproaches=False,\
		stats_max_k: int = 5,\
		DEBUG=False) -> None:
		"""
		Compute entity type-specific statistics and print them.
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

		# All the wikidata entity types annotated by the user
		#   as the correct ones, i.e. the set of all (correct) entity types
		#   occuring in the given corpus:
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

		print("===== Entity type-specific recalls " +\
			f"(using {'' if useTextualSurroundings else 'no '}text. surr., " +\
			f"{'' if useAttrNames else 'no '}attr. names and " +\
			f"{'' if useAttrExtensions else 'no '}attr. ext.): =====")

		print(Table.Table(surroundingText="",\
			headerRow=["Entity type", "# of occurrences"] +\
				[f"k={k}" for k in range(1, stats_max_k+1)],\
			columns=[[f"{entityType.entity_id} ({entityType.get_label()})"\
			for entityType in all_correct_wikidata_types]] +\
			[[str(len([None for tab, cl_res, corr_ent_type\
				in tables_with_classif_result_and_correct_entity_type\
				if corr_ent_type == entityType]))\
			 for entityType in all_correct_wikidata_types]] +\
			[["{:8.4f}%".format(100.0 * entity_type_specific_recall(k=k,\
						ranks_per_entity_type=ranks_per_entity_type,\
						entity_type=entityType))\
			  for entityType in all_correct_wikidata_types]\
			 for k in range(1, stats_max_k+1)]\
			).pretty_print(maxNumberOfTuples=\
				len(all_correct_wikidata_types)))

		print("===== Entity type-specific precisions " +\
			f"(using {'' if useTextualSurroundings else 'no '}text. surr., " +\
			f"{'' if useAttrNames else 'no '}attr. names and " +\
			f"{'' if useAttrExtensions else 'no '}attr. ext.): =====")

		print(Table.Table(surroundingText="",\
			headerRow=["Entity type", "# of occurrences"] +\
				[f"k={k}" for k in range(1, stats_max_k+1)],\
			columns=[[f"{entityType.entity_id} ({entityType.get_label()})"\
			for entityType in all_correct_wikidata_types]] +\
			[[str(len([None for tab, cl_res, corr_ent_type\
				in tables_with_classif_result_and_correct_entity_type\
				if corr_ent_type == entityType]))\
			 for entityType in all_correct_wikidata_types]] +\
			[["{:8.4f}%".format(100.0 * entity_type_specific_precision(k=k,\
						ranks_per_entity_type=ranks_per_entity_type,\
						tables_with_classif=tables_with_classif_fixed_params,\
						entity_type=entityType))\
			  for entityType in all_correct_wikidata_types]\
			 for k in range(1, stats_max_k+1)]\
			).pretty_print(maxNumberOfTuples=\
				len(all_correct_wikidata_types)))
