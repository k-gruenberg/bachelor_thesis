from typing import Dict, Any

from attr_names_to_ontology_class import get_dbpedia_properties


dbpediaPropertiesMappedToSBERTvector: Dict[str, Any] = {} 


def initalize_dbpedia_properties_mapped_to_SBERT_vector():
	dbpediaProperties: Dict[str, List[str]] = get_dbpedia_properties()

	# cf. https://www.sbert.net/docs/quickstart.html:
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer('all-MiniLM-L6-v2')

	for dbpedia_class, dbpedia_properties in dbpediaProperties.items():
		for dbpedia_property in dbpedia_properties:
			sbert_vector = model.encode(dbpedia_property)

			dbpediaPropertiesMappedToSBERTvector[dbpedia_property] =\
				sbert_vector


def get_dbpedia_properties_mapped_to_SBERT_vector() -> Dict[str, Any]:
	if dbpediaPropertiesMappedToSBERTvector == {}:
		initalize_dbpedia_properties_mapped_to_SBERT_vector()
	return dbpediaPropertiesMappedToSBERTvector
