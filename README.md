# bachelor_thesis
Python code for my bachelor thesis which is "An Evaluation of Strategies for Matching Entity Types to Table Tuples in the Context of Narratives"

## Examples

Filtering all the nouns from a given input text using the Oxford English dictionary and mapping them to a list of Wikidata entries using the Wikidata Web API:

```
$ python3 filter_nouns.py "2008 2009 2010 2011 2012 2013 2014 2013 Tulsa Golden Hurricane Receiving through 01/06/2014 Players Teams Conferences National Home @SportSourceA Contact Us Advertise? Receiving > Tulsa > 2013 Teams > Home You are here:"

Hurricane
1 storm with a violent wind, esp. A w. Indian cyclone. 2 meteorol. Wind of 65 knots (75 m.p.h.) Or more, force 12 on the beaufort scale. [spanish and portuguese from carib]
['Q58197759 (hurricane; group of tropical storms of the Atlantic and east Pacific basins with sustained wind speeds > 64 kt. Classified by Saffir–Simpson sale)', 'Q194251 (Hawker Hurricane; 1935 fighter aircraft family by Hawker)', 'Q482646 (Hurricane; city in Washington County, Utah, United States)', 'Q832732 (The Hurricane; 1999 film by Norman Jewison)', 'Q224325 (Hurricane; Wikimedia disambiguation page)', 'Q2649771 (Hurricane; city in West Virginia)', 'Q74590294 (Hurricane; Serbian R&B and pop girl group)']

Players
1 participant in a game. 2 person playing a musical instrument. 3 actor.
['Q937857 (association football player; person who plays association football (soccer) (note: do NOT use this together with "instance of", use it as "occupation" instead))', 'Q5276395 (gamer; person who plays video games and/or identifies with the gamer identity)', 'Q4197743 (player; person who plays a game)', 'Q18536342 (competitive player; player of a competitive sport or game)', 'Q1551573 (The Player; 1992 film by Robert Altman)', 'Q353589 (Player; Wikimedia disambiguation page)', 'Q378491 (Player; American rock band)']

Teams
[...]
```

Doing the same, but (a) using several heuristics to reduce the number of results (i.e. Wikidata entries) and (b) returning the remaining results as an ordered list:

```
$ python3 filter_nouns_with_heuristics.py "2008 2009 2010 2011 2012 2013 2014 2013 Tulsa Golden Hurricane Receiving through 01/06/2014 Players Teams Conferences National Home @SportSourceA Contact Us Advertise? Receiving > Tulsa > 2013 Teams > Home You are here:"
Q327245 (team; group linked in a common purpose)
Q58197759 (hurricane; group of tropical storms of the Atlantic and east Pacific basins with sustained wind speeds > 64 kt. Classified by Saffir–Simpson scale)
Q4197743 (player; person who plays a game)
Q625994 (convention; meeting of a group of individuals and/or companies in a certain field)
Q23797 (contact lens; very thin plastic lens worn directly on the eye to correct visual defects)
Q8418 (handball; team sport played with a thrown ball and goals)
Q194251 (Hawker Hurricane; 1935 fighter aircraft family by Hawker)
Q2992826 (athletic conference; collection of sports teams, playing competitively against each other, sometimes subdivided into divisions)
Q394001 (electrical contact; part of a component that reversibly forms an electrical connection)
```

For a given list of attribute names, return the list of DBpedia types whose property names best match the given input list of attribute names (similarity computed using Jaccard or SBERT):

```
$ python3 attr_names_to_ontology_class.py "Name" "Status" "County" "Population Census 1990-04-01"
1.6076923076923078 PopulatedPlace
1.2580645161290323 Place
1.2285714285714286 Person
0.804040404040404 Settlement
0.6666666666666666 Openswarm
0.6573426573426574 Island
0.6527777777777778 Work
0.5865465803546299 Athlete
0.5712121212121213 CelestialBody
0.5298701298701298 River
0.512280701754386 Species
0.4907407407407407 School
[...]
```

Use the 3-step approach described by Zwicklbauer et al. to generate an ordered list of Wikidata types for a given input list of names of instances of the type searched for:

```
$ python3 attr_extension_to_ontology_class.py "Jordan James" "Keevan Lucas" "Trey Watts" "Thomas Roberson"

##### Finished Step 1 - Cell entity annotation: #####
Jordan James: ['Q109638024 (Jordan James)', 'Q6276642 (Jordan James)', 'Q16220972 (Jordan James)', 'Q133760 (Jordan Spence)', 'Q3183695 (Jordan Gavaris)', 'Q26265164 (Jordy Ranft)', 'Q1037339 (Jordan Schafer)']
Keevan Lucas: ['Q108051662 (Keevan Lucas)']
Trey Watts: ['Q7839622 (Trey Watts)']
Thomas Roberson: []

##### Finished Step 2 - Entity-type resolution: #####
Jordan James: Q109638024: ['Q5']
Jordan James: Q6276642: ['Q5']
Jordan James: Q16220972: ['Q5']
Jordan James: Q133760: ['Q5']
Jordan James: Q3183695: ['Q5']
Jordan James: Q26265164: ['Q5']
Jordan James: Q1037339: ['Q5']
Keevan Lucas: Q108051662: ['Q5']
Trey Watts: Q7839622: ['Q5']

##### Finished Step 3 - Type aggregation: #####
(9) Q5 (human)
```

```
$ python3 attr_extension_to_ontology_class.py "chevrolet chevelle malibu" "buick skylark 320" "plymouth satellite" "amc rebel sst" "ford torino" "ford galaxie 500"
(5) Q3231690 (automobile model)
(1) Q1361017 (Ford Torino)
```

Perform a Bing web search on all given input strings and return the nouns occurring in the Bing result snippets, ordered by how often they occur in those snippets:

```
$ python3 attr_extension_to_ontology_class_web_search.py "Manuel Neuer" "Joshua Kimmich" "Kai Havertz" "Marco Reus" "Timo Werner" "Serge Gnabry" "Antonio Rüdiger"
(20) club
(14) german
(12) professional
(12) team
(12) player
(11) play
(10) national
(10) date
(10) league
(10) height
[...]
```

Match a given input bag of numerical values against all (DBpedia type, DBpedia numerical property) pairs using the Kolmogorov-Smirnov (KS) test:

```
$ ./numeric_attr_extension_to_ontology_property_rust 147 1994 75 480 --types /data/dbpedia/data/instance_types_en.ttl --properties /data/dbpedia/data/infobox_properties_mapped_en.ttl

[1/6] Parsing --types .ttl file...
[2/6] Parsing --properties .ttl file...
[3/6] Populating dictionary with parsed --types .ttl file...
[INFO] 4951371 DBpedia resources
[4/6] Populating dictionary with parsed --properties .ttl file...
[INFO] 53843 (DBpedia type, numeric DBpedia property) pairs
[INFO] Unsorted input bag = [147.0, 1994.0, 75.0, 480.0]
[5/6] Computing KS scores...
[6/6] Sorting results by KS score...

KS Score - DBpedia type - DBpedia property - Matched list

0.16666666666666669 - Spacecraft - dimensions - [62.400000000000006, 81.60000000000001, ..., 264, ..., 1828.8, 2460]
0.16666666666666674 - Weapon - effectiveRange - [0.0, 100.0, 200.0, 300.0, 1800.0, 2000.0]
0.17777777777777778 - Library - location - [1, 1, ..., 306, ..., 75001, 109189]
0.1875 - Aircraft - powerOriginal - [20, 30, ..., 240, ..., 240000, 330000]
0.19444444444444442 - Protein - c - [16, 99, ..., 190, ..., 1105, 2001]
0.1986754966887417 - Settlement - populationDensity - [5, 7.6, ..., 271.1, ..., 12136, 19526.3]
0.2 - MilitaryUnit - image - [7, 9, ..., 222, ..., 100204, 1987200]
0.2 - OfficeHolder - candidate3Votes - [0, 1, ..., 366, ..., 14166, 19896]
0.20000000000000007 - AdministrativeRegion - densityMi - [15, 80, ..., 319, ..., 1967, 2690]
0.20000000000000007 - Settlement - pages - [23, 42, ..., 384, ..., 701, 143144]
0.20238095238095233 - Building - currentTenants - [22, 31, ..., 242, ..., 1200, 2038]
0.20238095238095238 - MilitaryUnit - awardNotes - [1, 4, ..., 411, ..., 7948800, 8899200]
0.20588235294117652 - Automobile - length - [2, 2, ..., 183, ..., 353740, 1940225.25]
0.2098569157392687 - City - densityKm - [1.191, 3.7, ..., 262, ..., 20550, 22920]
0.21428571428571427 - Motorcycle - aka - [3, 6, ..., 400, ..., 860, 9898]
0.22093023255813954 - Noble - pages - [28, 42, ..., 259, ..., 722723, 722723]
0.2222222222222222 - Company - stores - [2, 18, ..., 300, ..., 517, 17094]
0.22222222222222224 - RailwayStation - address - [1, 1, ..., 267, ..., 4769, 4884]
0.22222222222222224 - Dam - plantCapacity - [1.04, 1.5, ..., 347.5, ..., 11233, 18700]
0.22222222222222232 - Organisation - address - [27, 50, ..., 355, ..., 5500, 211414]
0.22222222222222232 - Spacecraft - semimajorAxis - [1, 33, ..., 200, ..., 2000, 6700]
0.22222222222222232 - Building - before - [11, 21, ..., 411, ..., 62117, 63317]
0.2237569060773481 - Plant - kj - [24.76, 46, ..., 259, ..., 3080, 3701]
0.22435897435897434 - Island - widthM - [0.15, 1, ..., 400, ..., 3000, 5500]
0.22580645161290322 - University - profess - [1, 1.357, ..., 285, ..., 3000, 15229]
0.22650771388499302 - AdministrativeRegion - populationVillage - [0, 0, ..., 324, ..., 9686, 19164]
0.2272727272727273 - Scientist - page - [1, 1, ..., 343, ..., 947, 637638]
[...]
```

```
$ ./numeric_attr_extension_to_ontology_property_rust --csv-file ~/bachelor_thesis/uci-machine-learning-repository-auto-mpg.data.tsv --csv-column 3 --types /data/dbpedia/data/instance_types_en.ttl --properties /data/dbpedia/data/infobox_properties_mapped_en.ttl

[1/6] Parsing --types .ttl file...
[2/6] Parsing --properties .ttl file...
[3/6] Populating dictionary with parsed --types .ttl file...
[4/6] Populating dictionary with parsed --properties .ttl file...
[INFO] Unsorted input bag = [130, 165, ..., 53, ..., 79, 82]
[5/6] Computing KS scores...
[6/6] Sorting results by KS score...

KS Score - DBpedia type - DBpedia property - Matched list

0.11593078295957171 - FigureSkater - fsScore - [18.73, 24.75, ..., 99.24, ..., 219.48, 2011]
0.12159863945578231 - Mountain - decSun - [54, 54.7, ..., 90, ..., 168.7, 203.5]
0.12495361781076064 - AdministrativeRegion - longitude - [9.400833333333333, 66, ..., 89, ..., 2280, 3180]
0.1551020408163264 - Country - octPrecipitationMm - [0, 0.5, ..., 100, ..., 330.6, 352.3]
0.1641156462585034 - Mountain - janSun - [64, 66.3, ..., 104, ..., 184.8, 202.4]
0.1643394199785177 - City - yearRainDays - [13, 14.3, ..., 106.7, ..., 235.9, 246]
0.16530612244897952 - Country - novPrecipitationMm - [2.5, 3.8, ..., 104.2, ..., 261.7, 287.5]
0.16825799517602502 - Aircraft - cruiseSpeedMph - [0, 13.75, ..., 108, ..., 614, 620]
0.17228846594817693 - Volcano - longD - [6.84861, 8, ..., 103.62, ..., 178, 178]
0.17452940080141643 - River - sourceConfluenceLongD - [1.5357, 2, ..., 101, ..., 153, 153]
0.17475244535684098 - RollerCoaster - dropFt - [2, 2, ..., 90, ..., 400, 418]
0.17692076830732292 - Locomotive - maxspeed - [2, 5, ..., 100, ..., 215005, 215217218]
0.17695134926008327 - Town - junRainMm - [0, 0, ..., 85, ..., 1010.1, 2294]
0.1778451594160796 - RollerCoaster - duration - [0, 1, ..., 108, ..., 356, 393]
0.18 - Device - weight - [1.2, 2.6, ..., 105, ..., 189, 204]
0.1824391046741275 - Motorcycle - topSpeed - [9, 11.73, ..., 105, ..., 2006, 2010]
[...]
```
