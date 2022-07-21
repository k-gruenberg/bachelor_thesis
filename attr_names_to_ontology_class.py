# This program takes a list of attribute/column names as input and returns
# an ordered list of class candidates from the DBpedia ontology that have
# similarly named attributes.

# The DBpedia ontology is contained in the `ontology--DEV_type=orig.owl` file
#   (which was downloaded from
#    https://databus.dbpedia.org/ontologies/dbpedia.org/ontology--DEV).
# It is in XML format and looks like this:
#
# [...]
# <owl:Class rdf:about="http://dbpedia.org/ontology/Automobile">
#     [...]
#     <rdfs:subClassOf
#         rdf:resource="http://dbpedia.org/ontology/MeanOfTransportation"/>
#     <rdfs:subClassOf rdf:resource="http://schema.org/Product"/>
#     <prov:wasDerivedFrom
#         rdf:resource=
#             "http://mappings.dbpedia.org/index.php/OntologyClass:Automobile"/>
# </owl:Class>
# [...]
# <owl:DatatypeProperty rdf:about="http://dbpedia.org/ontology/enginePower">
#     <rdf:type
#         rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>
#     [...]
#     <rdfs:domain
#         rdf:resource="http://dbpedia.org/ontology/MeanOfTransportation"/>
#     <rdfs:range
#         rdf:resource="http://www.w3.org/2001/XMLSchema#positiveInteger"/>
#     <prov:wasDerivedFrom
#         rdf:resource=
#             "http://mappings.dbpedia.org/index.php/OntologyProperty:enginePower"/>
# </owl:DatatypeProperty>
# [...]
# <owl:ObjectProperty rdf:about="http://dbpedia.org/ontology/ceremonialCounty">
#     <rdf:type
#         rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>
#     <rdfs:label xml:lang="en">Ceremonial County</rdfs:label>
#     <rdfs:domain rdf:resource="http://dbpedia.org/ontology/PopulatedPlace"/>
#     <rdfs:range rdf:resource="http://dbpedia.org/ontology/PopulatedPlace"/>
#     <rdfs:subPropertyOf
#         rdf:resource=
#             "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#sameSettingAs"/>
#     <prov:wasDerivedFrom
#         rdf:resource
#             ="http://mappings.dbpedia.org/index.php/OntologyProperty:ceremonialCounty"/>
#     </owl:ObjectProperty>
# [...]
#
# https://docs.python.org/3/library/xml.etree.elementtree.html
#   describes how to parse an XML file in Python, see below.

import sys
from typing import Dict, List
import xml.etree.ElementTree as ET

# ****** Parameters: ******
USE_BETTER_SUM_FORMULA: bool = True
USE_SBERT_INSTEAD_OF_JACCARD: bool = False
VERBOSE = True

# Each DBpedia class mapped to its properties:
dbpediaProperties: Dict[str, List[str]] = {}

# Each DBpedia class mapped to its superclasses:
dbpediaSuperclasses: Dict[str, List[str]] = {}

# Now, fill `dbpediaProperties` and `dbpediaSubclasses`
#   with the information from the .owl file:
tree = ET.parse('ontology--DEV_type=orig.owl')
# Source of 'ontology--DEV_type=orig.owl' is:
#   https://databus.dbpedia.org/ontologies/dbpedia.org/ontology--DEV
root = tree.getroot()
for child in root:
	# E.g turn `{http://www.w3.org/2002/07/owl#}Class` into `Class`:
	tag = child.tag.split("}")[1]
	if tag == "Class":
		# E.g. extract the "Automobile" from the dictionary
		#   {'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about':
		#    'http://dbpedia.org/ontology/Automobile'}
		className: str =\
			[item[1].split("/")[-1]\
			 for item in child.attrib.items() if "about" in item[0]][0]
		if not className.isascii(): continue  # some names are in arabic
		subClassOf: List[str] =\
			[list(grandchild.attrib.values())[0].split("/")[-1]\
			for grandchild in child\
			if grandchild.tag.split("}")[1] == "subClassOf"]
		if className in dbpediaSuperclasses:
			dbpediaSuperclasses[className] += subClassOf
		else:
			dbpediaSuperclasses[className] = subClassOf
		#print("[Class] " + className + " [subClassOf] " + str(subClassOf))
	elif tag == "DatatypeProperty" or tag == "ObjectProperty":
		# E.g. extract the "enginePower" from the dictionary
		#   {'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about':
		#    'http://dbpedia.org/ontology/enginePower'}
		propertyName: str =\
			[item[1].split("/")[-1]\
			 for item in child.attrib.items() if "about" in item[0]][0]
		if not propertyName.isascii(): continue  # some names are in arabic
		domain =\
			[list(grandchild.attrib.values())[0].split("/")[-1]\
			for grandchild in child\
			if grandchild.tag.split("}")[1] == "domain"]#[0]
		if len(domain) > 1:
			print("alert: "\
				+ propertyName + " has multiple domains: " + str(domain))
		if len(domain) == 0: continue # a property that does not belong anywhere
		domain: str = domain[0]
		if not domain.isascii(): continue  # some names are in arabic
		if domain in dbpediaProperties:
			dbpediaProperties[domain] += [propertyName]
		else:
			dbpediaProperties[domain] = [propertyName]
		#print("[Property] " + propertyName + " [domain] " + domain)

if VERBOSE:
	print("[INFO] " + str(len(dbpediaProperties)) +\
		" DBpedia classes mapped to " +\
		str(sum(map(lambda lst: len(lst), dbpediaProperties.values()))) +\
		" properties")
	print("[INFO] " + str(len(dbpediaSuperclasses)) +\
		" DBpedia classes mapped to " +\
		str(sum(map(lambda lst: len(lst), dbpediaSuperclasses.values()))) +\
		" superclasses")

# Now that we have the DBpedia ontology, we can to the matching between
#   the `dbpediaProperties` and the input attribute names:

inputAttrNames: List[str] = sys.argv[1:]

# But first, we need to define a metric for word/attribute name similarity.
# For that, use...
# (a) the Jaccard similarity of the character trigrams;
#     as proposed by Pham et al.
#     in "Semantic Labeling: A Domain-Independent Approach" (ISWC 2016)
# (b) SBERT('s cosine similarity)
#     Links: Installation:
#              https://www.sbert.net/
#            Comparing Sentence Similarities:
#              https://www.sbert.net/docs/quickstart.html

model = None
if USE_SBERT_INSTEAD_OF_JACCARD:
	# *** For code below cf. https://www.sbert.net/docs/quickstart.html ***
	if VERBOSE: print("[INFO] Preparing SBERT...")
	from sentence_transformers import SentenceTransformer, util
	model = SentenceTransformer('all-MiniLM-L6-v2')
	if VERBOSE: print("[INFO] Prepared SBERT.")

# E.g. trigrams("Hello") == ['hel', 'ell', 'llo']
def trigrams(word: str) -> List[str]:
	return [word[i:i+3].lower() for i in range(0, len(word) - 2)]

# E.g. similarity("horsepower", "enginePower") == 0.3076923076923077
#      similarity("horsepower", "modelStartYear") == 0.0
#   when USE_SBERT_INSTEAD_OF_JACCARD = False,
#   i.e. when using Jaccard similarity of character trigrams.
def similarity(attrName1: str, attrName2: str) -> float:
	if not USE_SBERT_INSTEAD_OF_JACCARD:  # Use Jaccard and not SBERT:
		a = set(trigrams(attrName1))
		b = set(trigrams(attrName2))
		aIntersectB = a.intersection(b)
		aUnionB = a.union(b)
		return len(aIntersectB) / len(aUnionB)
	else:  # Use SBERT('s cosine similarity) instead of Jaccard similarity:
		# *** For code below cf. https://www.sbert.net/docs/quickstart.html ***	
		# Sentences are encoded by calling model.encode():
		emb1 = model.encode(attrName1)
		emb2 = model.encode(attrName2)
		# Compute Cosine-Similarity:
		cos_sim = util.cos_sim(emb1, emb2)
		return float(cos_sim)

# Each DBpedia class mapped to a score measuring how close its attribute names
#   fit the `inputAttrNames`:
dbpediaClassesWithMatchScore: Dict[str, float] = {}

print("[PROGRESS] " + str(len(dbpediaProperties)) +\
	  " classes to score: ", end="", flush=True)
for dbpediaClass in dbpediaProperties.keys():
	ontologyAttrNames = dbpediaProperties[dbpediaClass]
	
	if not USE_BETTER_SUM_FORMULA:
		# Score/Metric #1:
		# S(A_onto, A_data) = SIGMA(a in A_onto) max(a' in A_data) Jaccard(a, a')
		#
		# Results (when using Jaccard and not SBERT):
		# * "mpg" "cylinders" "displacement" "horsepower" "weight" "acceleration"
		#   "model year" "origin" "car name"
		#   14.416038295039662 Person
		#   10.235548695262871 PopulatedPlace
		#   9.896932262979936 Place
		#   4.7204906204906205 Engine (! plausible)
		#   3.987794052147431 MeanOfTransportation (!!! #5)
		#   3.685712972403385 Settlement
		#   3.6221840251252013 AutomobileEngine
		#   2.915719109216215 Athlete
		#   2.872721988679722 Island
		#   2.7356473145391575 SpaceMission
		#   1.8786159384355638 Organisation
		#   ...
		# * "horsepower" "model year"
		#   1.866265146388985 Place
		#   1.8491635286446604 PopulatedPlace
		#   1.810006350718425 MeanOfTransportation (!!! #3)
		#   1.4348966265832603 Person
		#   0.8267651236584727 ArchitecturalStructure
		#   ...
		# * "Name" "Status" "County" "Population Census 1990-04-01"
		#   "Population Census 2000-04-01" "Population Census 2010-04-01":
		#   11.145873174239679 PopulatedPlace (!!! #1)
		#   8.184887886689442 Person
		#   4.900212710648301 Place
		#   2.5578531403004576 Settlement
		#   1.9056646056646054 Island
		#   ...
		# * "Name" "Status" "County" "Population Census 1990-04-01"
		#   11.145873174239679 PopulatedPlace (!!! #1)
		#   8.184887886689442 Person
		#   4.900212710648301 Place
		#   2.5578531403004576 Settlement
		#   1.9056646056646054 Island
		#   ...
		dbpediaClassesWithMatchScore[dbpediaClass] =\
			sum(\
				[max([similarity(ontologyAttrName, inputAttrName)\
					for inputAttrName in inputAttrNames])\
				for ontologyAttrName in ontologyAttrNames]\
			)
	else:  # (Do use better sum formula:)
		# Score/Metric #2:
		# S(A_onto, A_data) = SIGMA(a in A_data) max(a' in A_onto) Jaccard(a, a')
		#
		# Advantage:
		# The amount of summands now depends on |A_data| instead of |A_onto|
		# and is therefore constant for all S(A_onto, A_data).
		#
		# Results (when using Jaccard and not SBERT):
		# * "mpg" "cylinders" "displacement" "horsepower" "weight" "acceleration"
		#   "model year" "origin" "car name"
		#   3.85064935064935 Engine (!! very plausible)
		#   2.712121212121212 AutomobileEngine
		#   2.4840857671740024 Person
		#   2.10226322590453 MeanOfTransportation (!!! #4)
		#   1.3764152514152512 Place
		#   1.2612146307798482 PopulatedPlace
		#   1.223245885969671 Athlete
		#   1.1267768780926675 School
		#   ...
		# * "horsepower" "model year"
		#   0.6923076923076923 MeanOfTransportation (!!! #1)
		#   0.4583333333333333 FictionalCharacter
		#   0.375 Sales
		#   0.34285714285714286 Place
		#   0.26785714285714285 PopulatedPlace
		#   0.2426470588235294 Athlete
		#   0.23333333333333334 School
		#   0.2222222222222222 SoccerPlayer
		#   ...
		# * "Name" "Status" "County" "Population Census 1990-04-01"
		#   "Population Census 2000-04-01" "Population Census 2010-04-01":
		#   2.223076923076923 PopulatedPlace (!!! #1)
		#   1.7741935483870968 Place
		#   1.5142857142857142 Person
		#   1.2484848484848485 Settlement
		#   0.96875 GeopoliticalOrganisation
		#   ...
		# * "Name" "Status" "County" "Population Census 1990-04-01"
		#   1.6076923076923078 PopulatedPlace (!!! #1)
		#   1.2580645161290323 Place
		#   1.2285714285714286 Person
		#   0.804040404040404 Settlement
		#   0.6666666666666666 Openswarm
		#   ...
		dbpediaClassesWithMatchScore[dbpediaClass] =\
			sum(\
				[max([similarity(ontologyAttrName, inputAttrName)\
					for ontologyAttrName in ontologyAttrNames])\
				for inputAttrName in inputAttrNames]\
			)
	print("|", end="", flush=True)  # print progress 
print("")  # newline after progress finished

# Now that we have a match score for each DBpedia class, we can print out all
#   of them with a match score >0; in descending order, i.e. highest match
#   score first:

for dbpediaClass, matchScore in\
	sorted(dbpediaClassesWithMatchScore.items(),\
		key=lambda item: item[1],\
		reverse=True):  # sort by score in descending order
	#Stop printing when the the first class with a match score of 0 is reached: 
	if matchScore == 0.0:
		break
	print(str(matchScore) + " " + dbpediaClass)
