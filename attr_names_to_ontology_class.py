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


# Now that we have the DBpedia ontology, we can to the matching between
#   the `dbpediaProperties` and the input attribute names:

inputAttrNames = sys.argv[1:]

# But first, we need to define a metric for word/attribute name similarity.
# Use the Jaccard similarity of the character trigrams for that;
#   as proposed by Pham et al.
#   in "Semantic Labeling: A Domain-Independent Approach" (ISWC 2016):

# E.g. trigrams("Hello") == ['hel', 'ell', 'llo']
def trigrams(word: str) -> List[str]:
	return [word[i:i+3].lower() for i in range(0, len(word) - 2)]

# E.g. similarity("horsepower", "enginePower") == 0.3076923076923077
#      similarity("horsepower", "modelStartYear") == 0.0
def similarity(attrName1: str, attrName2: str) -> float:
	a = set(trigrams(attrName1))
	b = set(trigrams(attrName2))
	aIntersectB = a.intersection(b)
	aUnionB= a.union(b)
	return len(aIntersectB) / len(aUnionB)

# Each DBpedia class mapped to a score measuring how close its attribute names
#   fit the `inputAttrNames`:
dbpediaClassesWithMatchScore: Dict[str, float] = {}
for dbpediaClass in dbpediaProperties.keys():
	ontologyAttrNames = dbpediaProperties[dbpediaClass]
	dbpediaClassesWithMatchScore[dbpediaClass] =\
		sum(\
			[max([similarity(ontologyAttrName, inputAttrName)\
				for inputAttrName in inputAttrNames])\
			for ontologyAttrName in ontologyAttrNames]\
		)
	# Example:
	# The match score for the DBpedia class "Automobile" and
	#   the (user-)input attribute names 
	#   "mpg" "cylinders" "displacement" "horsepower" "weight" "acceleration"
	#   "model year" "origin" "car name"
	#   is computed as follows:
	# ToDo


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
