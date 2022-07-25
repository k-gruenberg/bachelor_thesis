dbpediaClassesMappedToWikidata: Dict[str, str] = {}

# (1) Extract all DBpedia classes from .owl file:

# ToDo

# (2) Search Wikidata for every DBpedia class name.
#     Hopefully, one of the search results will have the
#     P1709 (equivalent class) property defined, containing the
#     equivalent DBpedia class:

# ToDo

print(\
	len(\
		list(filter(lambda v: v != "", dbpediaClassesMappedToWikidata.values()))
	) +\
	" out of " + len(dbpediaClassesMappedToWikidata) +\
	" DBpedia classes mapped to Wikidata entries:"\
	)
print("")
print(dbpediaClassesMappedToWikidata)