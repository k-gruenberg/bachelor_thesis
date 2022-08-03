# bachelor_thesis
Python code for my bachelor thesis which is "An Evaluation of Strategies for Matching Entity Types to Table Tuples in the Context of Narratives"

## Examples

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

```
$ python3 attr_extension_to_ontology_class.py "chevrolet chevelle malibu" "buick skylark 320" "plymouth satellite" "amc rebel sst" "ford torino" "ford galaxie 500"
(5) Q3231690 (automobile model)
(1) Q1361017 (Ford Torino)
```

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
