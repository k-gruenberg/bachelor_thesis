from typing import Dict, Any

dbpediaPropertiesMappedToSBERTvector: Dict[str, Any] = {} 

def initalize_dbpedia_properties_mapped_to_SBERT_vector():
	pass  # ToDo

def get_dbpedia_properties_mapped_to_SBERT_vector() -> Dict[str, Any]:
	if dbpediaPropertiesMappedToSBERTvector == {}:
		initalize_dbpedia_properties_mapped_to_SBERT_vector()
	return dbpediaPropertiesMappedToSBERTvector
