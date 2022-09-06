from typing import Dict, Any

# SBERT encodings:
# DBpedia properties (and other strings) mapped to SBERT vectores:
sbert_encodings: Dict[str, Any] = {}

model = None


def initialize_sbert_model():
	"""
	Initialize the SBERT model.

	=> You never have to call this function yourself, it is called
	   automatically in the cases where it is needed.
	"""

	global model
	if model is None:
		# cf. https://www.sbert.net/docs/quickstart.html:
		from sentence_transformers import SentenceTransformer
		model = SentenceTransformer('all-MiniLM-L6-v2')


def prepare_dbpedia_properties_mapped_to_SBERT_vector():
	"""
	Prepare the SBERT vectores for **all** DBpedia property names.
	This may take a while (approx. 1 minute) but computing SBERT
	similarites will be faster afterwards.

	=> You should call this function once in the beginning, or you don't.
	   However, if you don't, this preparation will take place implicitly
	   once the SBERT vectors for all DBpedia property name will be requested,
	   one after the other...
	"""

	from attr_names_to_ontology_class import get_dbpedia_properties

	dbpediaProperties: Dict[str, List[str]] = get_dbpedia_properties()

	initialize_sbert_model()

	for dbpedia_class, dbpedia_properties in dbpediaProperties.items():
		for dbpedia_property in dbpedia_properties:
			sbert_vector = model.encode(dbpedia_property)

			sbert_encodings[dbpedia_property] =\
				sbert_vector


def sbert_similarity(attrName1: str, attrName2: str) -> float:
	"""
	Compute the SBERT similarity of two attribute names.
	This will use the prepared SBERT vectores if
	prepare_dbpedia_properties_mapped_to_SBERT_vector() was called
	beforehand.
	If the respective vectors are not cached, they will be for the next
	time this function is called! (implicit preparation)

	=> This is the main function you want to use!
	"""

	initialize_sbert_model()

	# The two SBERT vectors for `attrName1` and `attrName2`:
	emb1 = sbert_encodings[attrName1]\
		if attrName1 in sbert_encodings\
		else sbert_encodings.setdefault(attrName1,\
			model.encode(attrName1))
	emb2 = sbert_encodings[attrName2]\
		if attrName2 in sbert_encodings\
		else sbert_encodings.setdefault(attrName2,\
			model.encode(attrName2))

	# Compute and return Cosine-Similarity:
	from sentence_transformers import util
	cos_sim = util.cos_sim(emb1, emb2)
	return float(cos_sim)


def get_initialized_sbert_model():
	global model
	initialize_sbert_model()
	return model


def get_possibly_uninitialized_sbert_model():
	global model
	return model
