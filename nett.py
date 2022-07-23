"""
NETT = Narrative Entity Type(s) to Tables

This program takes as input:
* a list of one or more entity types occuring in the narrative that is to be
  grounded (ideally as Wikidata ID's, otherwise as literal strings)
* a corpus of relational tables, either in CSV or in a specific JSON format
  (the files are allowed to be inside one or multiple .tar archives)
* various settings as parameters:
  - ...

And it produces as output:
* for each input entity type an ordered list of relational tables from the
  given corpus for which the program thinks that the tuples represent entities
  of that entity type
* the output is lazily printed to stdout in JSON format
"""

# ToDo: argparse
