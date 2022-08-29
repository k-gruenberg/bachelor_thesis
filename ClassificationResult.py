from __future__ import annotations
from typing import List, Dict, Any, Iterator, Set

from WikidataItem import WikidataItem
import Table

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
				 normalizeApproaches=False)\
				-> List[Tuple[float, WikidataItem]]:

		resultUsingTextualSurroundings: Dict[WikidataItem, float] =\
			self.resUsingTextualSurroundings

		resultUsingAttrNames: Dict[WikidataItem, float] =\
			self.resUsingAttrNames

		resultUsingAttrExtensions: Dict[WikidataItem, float] =\
			self.resUsingAttrExtensions

		if normalizeApproaches:
			resultUsingTextualSurroundings =\
				normalize(resultUsingTextualSurroundings)
			resultUsingAttrNames = normalize(resultUsingAttrNames)
			resultUsingAttrExtensions = normalize(resultUsingAttrExtensions)

		combinedResult: List[Tuple[float, WikidataItem]] = []

		combinedResult = combine3(\
			dct1=resultUsingTextualSurroundings,\
			weight1=textualSurroundingsWeighting,\
			dct2=resultUsingAttrNames,\
			weight2=attrNamesWeighting,\
			dct3=resultUsingAttrExtensions,\
			weight3=attrExtensionsWeighting,\
		)

		return combinedResult

	@classmethod
	def print_statistics(cls,\
		tables_with_classif_result_and_correct_entity_type_specified_by_user:\
		List[Tuple[Table, ClassificationResult,  WikidataItem]],\
		stats_max_k: int = 5) -> None:

		# 3 of 3 approaches:

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=True,
			useAttrExtensions=True
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=True,
			useAttrExtensions=True
		)
		print("")
		
		# 2 of 3 approaches:

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=True,
			useAttrExtensions=True
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=True,
			useAttrExtensions=True
		)
		print("")

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=False,
			useAttrExtensions=True
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=False,
			useAttrExtensions=True
		)
		print("")

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=True,
			useAttrExtensions=False
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=True,
			useAttrExtensions=False
		)
		print("")

		# 1 of 3 approaches:

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=False,
			useAttrExtensions=False
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=True,
			useAttrNames=False,
			useAttrExtensions=False
		)
		print("")

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=True,
			useAttrExtensions=False
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=True,
			useAttrExtensions=False
		)
		print("")

		ClassificationResult.print_statistics_overall(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=False,
			useAttrExtensions=True
		)
		print("")
		ClassificationResult.print_statistics_entity_type_specific(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user,
			stats_max_k=k,
			useTextualSurroundings=False,
			useAttrNames=False,
			useAttrExtensions=True
		)
		print("")
		

	@classmethod
	def print_statistics_overall(cls,\
		tables_with_classif_result_and_correct_entity_type_specified_by_user:\
		List[Tuple[Table, ClassificationResult,  WikidataItem]],\
		useTextualSurroundings: bool,\
		useAttrNames: bool,\
		useAttrExtensions: bool,
		stats_max_k: int = 5) -> None:  # ToDo: missing parameters!!!!! => use weightings given or always 1.0 ?!

		# Precomputations:

		number_of_tables: int = len(\
			tables_with_classif_result_and_correct_entity_type_specified_by_user)

		# (floats only to allow for infinity:)
		ranks: List[float] = None  # ToDo!!!

		ranks_per_entity_type: Dict[WikidataItem, List[float]] = None  # ToDo!!!

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
			[k\
			 for k in range(1, stats_max_k+1)],\
			[len([rank for rank in ranks if rank <= k]) / len(ranks)\
			 for k in range(1, stats_max_k+1)],\
			[sum(len(rank for rank in ranks if rank <= k) / len(ranks)\
			 for entityType, ranks in ranks_per_entity_type.items())\
			 / len(ranks_per_entity_type)\
			 for k in range(1, stats_max_k+1)]\
			]).pretty_print())

	@classmethod
	def print_statistics_entity_type_specific(cls,\
		tables_with_classif_result_and_correct_entity_type_specified_by_user:\
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
