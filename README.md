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

##### Finished Step 1 - Cell entity annotation: #####
chevrolet chevelle malibu: []
buick skylark 320: []
plymouth satellite: ['Q1808628 (Plymouth Satellite)']
amc rebel sst: []
ford torino: ['Q1361017 (Ford Torino)', 'Q1437002 (Ford Torino)', 'Q5467973 (Ford Torino Talladega)', 'Q90924026 (Ford Torino GT)', 'Q5467971 (Ford Torino Engine Specifications)']
ford galaxie 500: []

##### Finished Step 2 - Entity-type resolution: #####
plymouth satellite: Q1808628: ['Q3231690']
ford torino: Q1361017: ['Q3231690']
ford torino: Q1437002: ['Q3231690']
ford torino: Q5467973: ['Q3231690']
ford torino: Q90924026: ['Q3231690', 'Q1361017']
ford torino: Q5467971: None

##### Finished Step 3 - Type aggregation: #####
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
$ python3 numeric_attr_extension_to_ontology_property.py --csv-file uci-machine-learning-repository-auto-mpg.data.tsv --csv-column 0 --input dbpedia_numeric_attribute_extensions.tsv --compare-with Automobile: MeanOfTransportation: AutomobileEngine: Engine: :enginePower

[4/6] Populating dictionary with parsed --input TSV file...
[INFO] 53843 (DBpedia type, numeric DBpedia property) pairs
[INFO] Unsorted input bag = [18.0, 15.0, ..., 20.0, ..., 28.0, 31.0]
[5/6] Computing KS scores...
[6/6] Sorting results by KS score...

KS Score - DBpedia type - DBpedia property - Matched list

0.06838569903596248 - Settlement - sepHighC - [0.0, 0.2, ..., 23.0, ..., 43.7, 285.0]
0.08317446679702123 - Settlement - mayHighC - [0.0, 0.0, ..., 21.5, ..., 44.4, 255.0]
0.08372156912123252 - City - octHighC - [0.0, 1.6, ..., 22.3, ..., 38.1, 39.1]
0.09217964824120606 - BasketballTeam - q - [8.0, 10.0, ..., 23.0, ..., 35.0, 39.0]
0.09301200839880153 - AmericanFootballPlayer - wonderlic - [4.0, 6.0, ..., 24.0, ..., 48.0, 49.0]
0.09444519896781212 - Village - sepHighC - [5.3, 7.2, ..., 20.5, ..., 40.0, 42.8]
0.09993748647543932 - AdministrativeRegion - aprHighC - [0.8, 1.0, ..., 23.5, ..., 36.8, 41.0]
0.10015461925009664 - Town - mayRecordLowF - [3.0, 4.0, ..., 22.0, ..., 63.0, 64.0]
0.1004555656471362 - Drug - h - [1.0, 1.0, ..., 22.0, ..., 12124.0, 60189.0]
0.10362418151362876 - Diocese - territory - [10.0, 10.0, ..., 23.0, ..., 39.0, 48.0]
[...]
0.19762546703094955 - Settlement - augHighC - [1.5, 3.1, ..., 25.7, ..., 47.2, 321.0]
0.19885139985642497 - Mountain - aprRecordHighC - [13.7, 13.8, ..., 22.7, ..., 29.0, 31.4]

===== Additional comparisons as specified by the user: =====
0.26583738363950904 - Automobile - pedestrianPoints - [8.0, 10.0, ..., 21.0, ..., 29.0, 33.7]
0.40516072425620164 - Automobile - battery - [0.6, 0.9, ..., 16.5, ..., 99.0, 607085.0]
0.4179229480737018 - Automobile - fuelCapacity - [8.0, 17.2, 120.0]
0.42386173290695905 - Automobile - adultScore - [15.0, 18.0, ..., 29.0, ..., 35.0, 36.0]
0.4355108877721943 - Automobile - fuelEconomy - [17.5, 30.0, 31.0]
[...]
1.0 - AutomobileEngine - year - [2014.0]
0.9280756724800473 - Weapon - enginePower - [1.0, 1.0, ..., 241.0, ..., 10200.0, 20053.0]
1.0 - Automobile - enginePower - [350.0]
```

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

## NETT

NETT is short for "Narrative Entity Type(s) to Tables" and is a tool for semantic labeling *(as defined by Ramnandan et al.)* of tables in CSV, XLSX or the JSON format used by the WDC Web Table Corpus. It has 4 different modes:

### Mode (1):

Generate (lots of) statistics (on how good NETT is) for a given corpus, by classifying each table in the corpus manually and automatically:

```
$ python3 nett.py --corpus test_corpus --sbert --stats --stats-max-k 11

========== Statistics (based on 10 manual classifications): ==========

===== Overall stats (using all 3 approaches with w1=1.0, w2=1.0, w3=1.0): =====
MRR: 0.80625
k   | Top-k coverage (%) | Recall (%), macro-average | Precision (%), macro-avg. | F1 score (F1 of avg. prec. & avg. rec.) | F1 score (Avg. of class-wise F1 scores)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
1   |  80.0000           |  75.0000                  | 100.0000                  | 0.857143                                | 1.000000                               
2   |  80.0000           |  75.0000                  | 100.0000                  | 0.857143                                | 1.000000                               
3   |  80.0000           |  75.0000                  |  93.3333                  | 0.831683                                | 0.958333                               
4   |  80.0000           |  75.0000                  |  85.0000                  | 0.796875                                | 0.902778                               
5   |  80.0000           |  75.0000                  |  85.0000                  | 0.796875                                | 0.902778                               
6   |  80.0000           |  75.0000                  |  83.3333                  | 0.789474                                | 0.888889                               
7   |  80.0000           |  75.0000                  |  83.3333                  | 0.789474                                | 0.888889                               
8   |  80.0000           |  75.0000                  |  81.2500                  | 0.780000                                | 0.868687                               
9   |  80.0000           |  75.0000                  |  81.2500                  | 0.780000                                | 0.868687                               
10  |  80.0000           |  75.0000                  |  81.2500                  | 0.780000                                | 0.868687                               
11  |  80.0000           |  75.0000                  |  81.2500                  | 0.780000                                | 0.868687                               
Top-k coverage for different weightings of the 3 approaches (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):
     |        | w1=0.0      | w1=0.1      | w1=0.2      | w1=0.3      | w1=0.4      | w1=0.5      | w1=0.6      | w1=0.7      | w1=0.8      | w1=0.9      | w1=1.0     
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
k=1  | w2=0.0 |  50% /  50% |  60% /  60% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  70% /  80%
k=1  | w2=0.1 |  50% /  50% |  50% /  60% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  50% /  80%
k=1  | w2=0.2 |  50% /  50% |  50% /  60% |  50% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  70% /  80% |  50% /  80%
k=1  | w2=0.3 |  50% /  50% |  50% /  60% |  50% /  70% |  50% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  50% /  80% |  50% /  70%
k=1  | w2=0.4 |  50% /  50% |  50% /  60% |  50% /  70% |  50% /  70% |  50% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  80% |  50% /  80% |  50% /  70%
k=1  | w2=0.5 |  50% /  50% |  50% /  50% |  50% /  70% |  50% /  70% |  50% /  70% |  50% /  70% |  60% /  70% |  60% /  70% |  60% /  80% |  50% /  70% |  50% /  70%
k=1  | w2=0.6 |  50% /  50% |  50% /  50% |  50% /  70% |  50% /  70% |  50% /  70% |  50% /  70% |  50% /  70% |  60% /  80% |  50% /  70% |  50% /  70% |  50% /  70%
k=1  | w2=0.7 |  50% /  50% |  50% /  50% |  50% /  70% |  50% /  70% |  50% /  70% |  50% /  70% |  40% /  70% |  50% /  80% |  50% /  70% |  50% /  70% |  50% /  70%
k=1  | w2=0.8 |  50% /  50% |  50% /  50% |  50% /  70% |  50% /  70% |  40% /  70% |  40% /  70% |  40% /  70% |  50% /  70% |  40% /  70% |  50% /  70% |  50% /  60%
k=1  | w2=0.9 |  50% /  50% |  50% /  50% |  40% /  70% |  40% /  70% |  40% /  70% |  40% /  70% |  40% /  80% |  40% /  70% |  40% /  70% |  40% /  60% |  50% /  60%
k=1  | w2=1.0 |  40% /  50% |  40% /  50% |  40% /  60% |  40% /  70% |  30% /  70% |  30% /  60% |  40% /  70% |  40% /  70% |  40% /  60% |  40% /  60% |  40% /  40%
k=2  | w2=0.0 |  50% /  50% |  60% /  60% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  80% /  80%
k=2  | w2=0.1 |  50% /  50% |  60% /  60% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  60% /  70% |  80% /  80%
[...]
k=11 | w2=0.9 |  50% /  50% |  50% /  60% |  60% /  80% |  60% /  80% |  60% /  80% |  60% /  80% |  80% /  80% |  70% /  80% |  70% /  80% |  70% /  70% |  70% /  70%
k=11 | w2=1.0 |  50% /  50% |  50% /  60% |  60% /  80% |  60% /  80% |  60% /  80% |  50% /  80% |  50% /  80% |  70% /  80% |  70% /  70% |  70% /  70% |  70% /  60%
Recall, macro-avg. for diff. weightings of the 3 approaches (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):
     |        | w1=0.0      | w1=0.1      | w1=0.2      | w1=0.3      | w1=0.4      | w1=0.5      | w1=0.6      | w1=0.7      | w1=0.8      | w1=0.9      | w1=1.0     
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
k=1  | w2=0.0 |  38% /  38% |  50% /  50% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  62% /  75%
k=1  | w2=0.1 |  38% /  38% |  38% /  50% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  46% /  75%
k=1  | w2=0.2 |  38% /  38% |  38% /  50% |  38% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  62% /  75% |  46% /  75%
k=1  | w2=0.3 |  38% /  38% |  38% /  50% |  38% /  62% |  38% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  38% /  75% |  46% /  62%
k=1  | w2=0.4 |  38% /  38% |  38% /  50% |  38% /  62% |  38% /  62% |  38% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  75% |  38% /  75% |  46% /  62%
k=1  | w2=0.5 |  38% /  38% |  38% /  38% |  38% /  62% |  38% /  62% |  38% /  62% |  38% /  62% |  50% /  62% |  50% /  62% |  50% /  75% |  38% /  62% |  46% /  62%
k=1  | w2=0.6 |  38% /  38% |  38% /  38% |  38% /  62% |  38% /  62% |  38% /  62% |  38% /  62% |  38% /  62% |  50% /  75% |  38% /  62% |  38% /  62% |  46% /  62%
k=1  | w2=0.7 |  38% /  38% |  38% /  38% |  38% /  62% |  38% /  62% |  38% /  62% |  38% /  62% |  25% /  62% |  38% /  75% |  38% /  62% |  38% /  62% |  46% /  62%
k=1  | w2=0.8 |  38% /  38% |  38% /  38% |  38% /  62% |  38% /  62% |  25% /  62% |  25% /  62% |  25% /  62% |  38% /  62% |  25% /  62% |  38% /  62% |  46% /  50%
k=1  | w2=0.9 |  38% /  38% |  38% /  38% |  25% /  62% |  25% /  62% |  25% /  62% |  25% /  62% |  25% /  75% |  25% /  62% |  25% /  62% |  25% /  50% |  46% /  50%
k=1  | w2=1.0 |  25% /  38% |  25% /  38% |  25% /  50% |  25% /  62% |  12% /  62% |  12% /  50% |  25% /  62% |  25% /  62% |  25% /  50% |  25% /  50% |  33% /  42%
k=2  | w2=0.0 |  38% /  38% |  50% /  50% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  75% /  75%
k=2  | w2=0.1 |  38% /  38% |  50% /  50% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  50% /  62% |  75% /  75%
[...]
k=11 | w2=0.9 |  38% /  38% |  38% /  50% |  50% /  75% |  50% /  75% |  50% /  75% |  50% /  75% |  75% /  75% |  62% /  75% |  62% /  75% |  62% /  62% |  62% /  62%
k=11 | w2=1.0 |  38% /  38% |  38% /  50% |  50% /  75% |  50% /  75% |  50% /  75% |  38% /  75% |  38% /  75% |  62% /  75% |  62% /  62% |  62% /  62% |  62% /  50%
MRR for diff. weightings of the 3 approaches (normalized/non-normalized; w3 such that w1+w2+w3 == 2.0):
       | w1=0.0      | w1=0.1      | w1=0.2      | w1=0.3      | w1=0.4      | w1=0.5      | w1=0.6      | w1=0.7      | w1=0.8      | w1=0.9      | w1=1.0     
----------------------------------------------------------------------------------------------------------------------------------------------------------------
w2=0.0 | .504 / .504 | .631 / .628 | .635 / .706 | .641 / .709 | .643 / .716 | .652 / .722 | .652 / .727 | .668 / .735 | .668 / .735 | .668 / .735 | .752 / .802
w2=0.1 | .506 / .506 | .586 / .632 | .637 / .712 | .641 / .715 | .648 / .721 | .653 / .727 | .661 / .732 | .670 / .739 | .670 / .739 | .669 / .739 | .653 / .805
w2=0.2 | .506 / .506 | .515 / .631 | .590 / .710 | .646 / .715 | .654 / .722 | .654 / .732 | .670 / .732 | .670 / .740 | .670 / .740 | .736 / .808 | .653 / .807
w2=0.3 | .507 / .506 | .512 / .640 | .535 / .711 | .596 / .717 | .654 / .727 | .662 / .732 | .670 / .741 | .670 / .742 | .687 / .740 | .653 / .807 | .653 / .756
w2=0.4 | .507 / .506 | .514 / .640 | .522 / .712 | .552 / .717 | .612 / .726 | .662 / .732 | .671 / .740 | .687 / .740 | .704 / .808 | .654 / .808 | .654 / .757
w2=0.5 | .507 / .506 | .512 / .591 | .523 / .713 | .534 / .717 | .558 / .730 | .621 / .740 | .671 / .740 | .687 / .740 | .704 / .807 | .654 / .758 | .612 / .758
w2=0.6 | .507 / .506 | .512 / .591 | .520 / .713 | .533 / .721 | .548 / .729 | .582 / .738 | .637 / .740 | .687 / .807 | .629 / .757 | .612 / .756 | .601 / .757
w2=0.7 | .507 / .506 | .511 / .567 | .522 / .715 | .527 / .725 | .536 / .738 | .579 / .738 | .549 / .738 | .629 / .806 | .624 / .757 | .588 / .757 | .581 / .723
w2=0.8 | .507 / .506 | .511 / .557 | .522 / .715 | .523 / .729 | .491 / .738 | .483 / .738 | .510 / .755 | .571 / .755 | .535 / .731 | .581 / .723 | .579 / .646
w2=0.9 | .507 / .506 | .510 / .564 | .466 / .721 | .456 / .729 | .473 / .738 | .469 / .754 | .486 / .804 | .465 / .730 | .488 / .720 | .525 / .642 | .565 / .641
w2=1.0 | .457 / .506 | .443 / .564 | .449 / .674 | .451 / .738 | .398 / .738 | .397 / .704 | .450 / .729 | .452 / .725 | .455 / .657 | .473 / .639 | .497 / .513
The optimal MRR of 0.8083333333333332 is achieved for w1=0.7, w2=0.3, w3=0.6, normalize=False!

===== Entity type-specific recalls (using text. surr., attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q75178 (auxiliary bishop) | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q11707 (restaurant)       | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q170584 (project)         | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q5 (human)                | 3                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
===== Entity type-specific precisions (using text. surr., attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q75178 (auxiliary bishop) | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q11707 (restaurant)       | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q170584 (project)         | 1                | 100.0000% | 100.0000% | 100.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q5 (human)                | 3                | 100.0000% | 100.0000% |  60.0000% |  60.0000% |  60.0000% |  50.0000% |  50.0000% |  37.5000% |  37.5000% |  37.5000% |  37.5000%

===== Overall stats (using attr. names (w2=1.0) & attr. ext. (w3=1.0)): =====
MRR: 0.5054012345679013
k   | Top-k coverage (%) | Recall (%), macro-average | Precision (%), macro-avg. | F1 score (F1 of avg. prec. & avg. rec.) | F1 score (Avg. of class-wise F1 scores)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
1   |  50.0000           |  37.5000                  |  91.6667                  | 0.532258                                | 0.952381                               
2   |  50.0000           |  37.5000                  |  86.6667                  | 0.523490                                | 0.916667                               
3   |  50.0000           |  37.5000                  |  80.9524                  | 0.512563                                | 0.866667                               
4   |  50.0000           |  37.5000                  |  79.1667                  | 0.508929                                | 0.848485                               
5   |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
6   |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
7   |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
8   |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
9   |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
10  |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
11  |  50.0000           |  37.5000                  |  77.7778                  | 0.506024                                | 0.833333                               
Top-k coverage for different weightings of the 2 approaches (normalized/non-normalized):
     | w2=0.0      | w2=0.1      | w2=0.2      | w2=0.3      | w2=0.4      | w2=0.5      | w2=0.6      | w2=0.7      | w2=0.8      | w2=0.9      | w2=1.0     
--------------------------------------------------------------------------------------------------------------------------------------------------------------
k=1  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  50% |  30% /  40% |  30% /  40% |  30% /  40% |  20% /  20%
k=2  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=3  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=4  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=5  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=6  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=7  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=8  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  30% /  40% |  30% /  30%
k=9  |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  40% /  40% |  30% /  30%
k=10 |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  40% /  40% |  40% /  40%
k=11 |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  50% /  50% |  40% /  50% |  40% /  40% |  40% /  40% |  40% /  40%
Recall, macro-avg. for diff. weightings of the 2 approaches (normalized/non-normalized):
     | w2=0.0      | w2=0.1      | w2=0.2      | w2=0.3      | w2=0.4      | w2=0.5      | w2=0.6      | w2=0.7      | w2=0.8      | w2=0.9      | w2=1.0     
--------------------------------------------------------------------------------------------------------------------------------------------------------------
k=1  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  38% |  12% /  25% |  12% /  25% |  12% /  25% |   8% /   8%
k=2  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=3  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=4  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=5  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=6  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=7  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=8  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  12% /  25% |  12% /  12%
k=9  |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  25% /  25% |  12% /  12%
k=10 |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  25% /  25% |  25% /  25%
k=11 |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  38% /  38% |  25% /  38% |  25% /  25% |  25% /  25% |  25% /  25%

===== Entity type-specific recalls (using no text. surr., attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q75178 (auxiliary bishop) | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q11707 (restaurant)       | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q170584 (project)         | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q5 (human)                | 3                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
===== Entity type-specific precisions (using no text. surr., attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q75178 (auxiliary bishop) | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q11707 (restaurant)       | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q170584 (project)         | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q5 (human)                | 3                |  75.0000% |  60.0000% |  42.8571% |  37.5000% |  33.3333% |  33.3333% |  33.3333% |  33.3333% |  33.3333% |  33.3333% |  33.3333%

[...]

===== Overall stats (using attr. ext. only): =====
MRR: 0.4
k   | Top-k coverage (%) | Recall (%), macro-average | Precision (%), macro-avg. | F1 score (F1 of avg. prec. & avg. rec.) | F1 score (Avg. of class-wise F1 scores)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
1   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
2   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
3   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
4   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
5   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
6   |  40.0000           |  33.3333                  |  88.8889                  | 0.484848                                | 0.888889                               
7   |  40.0000           |  33.3333                  |  83.3333                  | 0.476190                                | 0.857143                               
8   |  40.0000           |  33.3333                  |  83.3333                  | 0.476190                                | 0.857143                               
9   |  40.0000           |  33.3333                  |  83.3333                  | 0.476190                                | 0.857143                               
10  |  40.0000           |  33.3333                  |  83.3333                  | 0.476190                                | 0.857143                               
11  |  40.0000           |  33.3333                  |  83.3333                  | 0.476190                                | 0.857143                               

===== Entity type-specific recalls (using no text. surr., no attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q75178 (auxiliary bishop) | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q11707 (restaurant)       | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q170584 (project)         | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000% |   0.0000%
Q5 (human)                | 3                |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667%
===== Entity type-specific precisions (using no text. surr., no attr. names and attr. ext.): =====
Entity type               | # of occurrences | k=1       | k=2       | k=3       | k=4       | k=5       | k=6       | k=7       | k=8       | k=9       | k=10      | k=11     
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q855769 (strain)          | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q75178 (auxiliary bishop) | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q11707 (restaurant)       | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q170584 (project)         | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q134556 (single)          | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q1093829 (city of the Uni | 1                | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 100.0000%
Q13186 (raisin)           | 1                |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan% |      nan%
Q5 (human)                | 3                |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  66.6667% |  50.0000% |  50.0000% |  50.0000% |  50.0000% |  50.0000%
```

### Mode (2):

Generate statistics on the effects that using narrative knowledge has on precision and recall, by classifying each table in the corpus manually and automatically:

```
$ python3 nett.py Q5 --corpus test_corpus_6_wdc_only --jaccard --stats --co-occurring-keywords "math" --attribute-cond "year > 1900" --stats-max-k 100

===== Statistics (with and without narrative knowledge): =====
Looked for tables containing one of the following entity types: [Q5 (human)]
...with one of the following co-occurring keywords: ['math']
...and fulfilling the following attribute conditions (strictness 1.0): ['year > 1900']
Out of the 6 tables manually annotated, 2 were annotated with one of the entity types from [Q5 (human)].

In total, there were 4 (definitely) correct and 1 (possibly) incorrect rejections using the narrative restrictions.

========== k=1: ==========
# of tables retrieved using k=1 w/o narrative conditions: 2
# of tables retrieved using k=1 with narrative conditions: 1

True positives w/o narrative conditions: 2
True positives with narrative conditions: 1

Recall for [Q5 (human)], w/o narrative conditions: 100.0%
Recall for [Q5 (human)], with narrative conditions: 50.0%
Δ Recall (by using narrative knowledge): -50.0%

Precision for [Q5 (human)], w/o narrative conditions: 100.0%
Precision for [Q5 (human)], with narrative conditions: 100.0%
Δ Precision (by using narrative knowledge): 0.0%

========== k=2: ==========
[...]

========== k=100: ==========
# of tables retrieved using k=100 w/o narrative conditions: 4
# of tables retrieved using k=100 with narrative conditions: 1

True positives w/o narrative conditions: 2
True positives with narrative conditions: 1

Recall for [Q5 (human)], w/o narrative conditions: 100.0%
Recall for [Q5 (human)], with narrative conditions: 50.0%
Δ Recall (by using narrative knowledge): -50.0%

Precision for [Q5 (human)], w/o narrative conditions: 50.0%
Precision for [Q5 (human)], with narrative conditions: 100.0%
Δ Precision (by using narrative knowledge): 50.0%
```

### Mode (3):

Classify all tables in a given corpus:

```
$ python3 nett.py --corpus test_corpus --jaccard -k 2
test_corpus/UCI_Raisin_Dataset.xlsx: [(2.5873015873015874, 'Q17334923', 'location'), (1.7290043290043289, 'Q486972', 'human settlement')]
test_corpus/UCI_bank.csv: [(2.7738206238206238, 'Q5', 'human'), (2.4472222222222224, 'Q486972', 'human settlement')]
wdc_bishop.json: [(32.0, 'Q75178', 'auxiliary bishop'), (16.0, 'Q49476', 'archbishop')]
wdc_mutations.json: [(11.0, 'Q855769', 'strain'), (6.3307692307692305, 'Q7187', 'gene')]
test_corpus/wdc_thesis_places_in_Brown_county.json: [(8.0, 'Q1093829', 'city of the United States'), (6.0, 'Q2625603', 'population')]
test_corpus/wdc_thesis_players.json: [(30.883333333333333, 'Q5', 'human'), (3.0, 'Q327245', 'team')]
test_corpus/wdc_thesis_projects.json: [(13.57473604826546, 'Q170584', 'project'), (13.409744373560162, 'Q6256', 'country')]
test_corpus/wdc_thesis_restaurants.json: [(3.0, 'Q161380', 'credit card'), (1.5, 'Q2995644', 'result')]
test_corpus/wdc_thesis_songs_by_billy_squier.json: [(11.0, 'Q134556', 'single'), (8.91025641025641, 'Q482994', 'album')]
test_corpus/wdc_thesis_students.json: [(46.77142857142857, 'Q5', 'human'), (5.0, 'Q48282', 'student')]
```

### Mode (4):

Search a given corpus for tables containing tuples of the given entity type(s)...:

```
$ python3 nett.py Q5 --corpus test_corpus --jaccard -k 2
test_corpus/UCI_bank.csv: [(2.7738206238206238, 'Q5', 'human'), (2.4472222222222224, 'Q486972', 'human settlement')]
test_corpus/wdc_thesis_players.json: [(30.883333333333333, 'Q5', 'human'), (3.0, 'Q327245', 'team')]
test_corpus/wdc_thesis_students.json: [(46.77142857142857, 'Q5', 'human'), (5.0, 'Q48282', 'student')]
```

...possibly using some further narrative knowledge with the `--co-occurring-keywords` and/or `--attribute-cond` arguments:

```
$ python3 nett.py Q5 --corpus test_corpus --jaccard -k 2 --co-occurring-keywords "math" --attribute-cond "year > 1900"
test_corpus/wdc_thesis_students.json: [(46.77142857142857, 'Q5', 'human'), (5.0, 'Q48282', 'student')]
```

...yields one result while the following two calls do not yield any results:

```
$ python3 nett.py Q5 --corpus test_corpus --jaccard -k 2 --co-occurring-keywords "biology" --attribute-cond "year > 1900"
```

```
$ python3 nett.py Q5 --corpus test_corpus --jaccard -k 2 --co-occurring-keywords "math" --attribute-cond "year > 2000"
```
