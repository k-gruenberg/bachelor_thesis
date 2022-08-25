from typing import Dict

dbpediaClassesMappedToWikidata: Dict[str, str] = {}  # ToDo

def get_dbpedia_classes_mapped_to_wikidata() -> Dict[str, str]:
 	return dbpediaClassesMappedToWikidata

if __name__ == "__main__":
	main()

def main():
	RAWdbpediaClassesMappedToWikidata: Dict[str, str] = {}
	# Not to be confused with the manually curated (and static)
	#   `dbpediaClassesMappedToWikidata` above!
	# This main() exists to create a skelton dictionary that takes less time
	#   to complete manually than to create one from scratch, manually.

	# (1) Extract all DBpedia classes from .owl file:

	# ToDo

	# (2) Search Wikidata for every DBpedia class name.
	#     Hopefully, one of the search results will have the
	#     P1709 (equivalent class) property defined, containing the
	#     equivalent DBpedia class:

	# ToDo

	# (3) Print result:

	print(\
		len(\
			list(filter(lambda v: v != "",\
				RAWdbpediaClassesMappedToWikidata.values()))
		) +\
		" out of " + len(dbpediaClassesMappedToWikidata) +\
		" DBpedia classes mapped to Wikidata entries:"\
		)
	print("")
	print(RAWdbpediaClassesMappedToWikidata)
