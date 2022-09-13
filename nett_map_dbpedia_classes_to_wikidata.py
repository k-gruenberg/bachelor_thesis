from typing import Dict

from attr_names_to_ontology_class import get_dbpedia_properties
from WikidataItem import WikidataItem


# * 97 out of 283 DBpedia classes could be mapped to Wikidata entries
#   automatically using the code found in main() below.
# * All 44 mappings to "Q5" (human) were done manually.
#   -> 29 of those Q5 mappings were to DBpedia classes that had no
#      automatic mapping (see "(manual)" comments).
#   -> 15 of those Q5 mapping were to DBpedia classes that already
#      **had** a more specific automatic mapping that we replaced with the more
#      generic Q5 one (the reason being that the "Using Attribute Extensions"
#      approach will also yield only Q5 for humans, no matter their profession);
#      see "replaced automatic '...' with 'Q5'" comments.
# * There are 20 further "(manual)" mappings, the rest is deemed unimportant
#   enough to save the manual effort. When mapping, we paid attention to use
#   the Wikidata classes which are actually being used for the instance-of
#   relationships, so that this approach of "Using Attribute Names" works well
#   together with the approach of "Using Attribute Extensions"!
# * In total, there are -  82=97-15 automatic mappings, left as they were
#                       -  15 automatic mappings generified to 'Q5' (human)
#                       -  29 manual mappings to 'Q5' (human)
#                       -  69 further manual mappings (all carefully chosen)
#                          (29 of those were to mappings that the automatic program didn't find simply because it were two words concatenated into one...)
#                       -  56 further manual mappings (less(!) carefully chosen w/o testing instances; they should all have a subclass-of property (P279) though!; recognizable using "#####" instead of "(manual)")      
#                       -  32 DBpedia classes w/o Wikidata mappings because not applicable (recognizable using "N/A")
#                   SUM = 283 DBpedia classes
dbpediaClassesMappedToWikidata: Dict[str, str] =\
{
	'Legislature': 'Q11204',
	'GrandPrix': 'Q1089579',  # Q1089579 = "Grand Prix motor racing"  #####
	'Athlete': 'Q5',  # (manual)
	'Person': 'Q5',  # replaced automatic 'Q215627' with 'Q5'  (Wikidata says "use Q5 for humans" in description for person (Q215627) and according to https://dbpedia.org/ontology/Person, both Q215627 and Q5 are equivalent to dbo:Person)
	'Settlement': 'Q486972',
	'PopulatedPlace': 'Q486972',  # Q486972 = "human settlement"  # (manual)
	'SpaceMission': 'Q2133344',  # Q2133344 = "space mission"  # (manual)  # Instance tested: Apollo 13 (Q182252) => human spaceflight (Q752783) => space mission (Q2133344)  # Q2133344.P1709 == "http://dbpedia.org/ontology/SpaceMission"
	'Organisation': 'Q43229',
	'Species': 'Q7432',  # Q7432 = "species"  #####
	'Place': 'Q17334923',
	'Station': 'Q12819564',
	'FormulaOneRacer': 'Q5',  # (manual)
	'Planet': 'Q634',
	'PokerPlayer': 'Q5',  # (manual)
	'WrittenWork': 'Q47461344',  # Q47461344 = "written work"  # (manual)
	'Department': 'Q643589',  # Q643589 = "department"  # (manual)  # Instance tested: Aveyron (Q3216) => department of France (Q6465) => department (Q643589) ; Creuse (Q3353) => department of France (Q6465) => department (Q643589)
	'Canal': 'Q12284',  # Q12284 = "canal"  # (manual)  # Instances tested: Erie Canal (Q459578) => canal (Q12284) ; Mittelland Canal (Q48480) => summit level canal (Q2936105) => canal (Q12284)
	'Reference': '',  # N/A
	'SkiResort': 'Q130003',  # Q130003 = "ski resort"  #####
	'Comedian': 'Q5',  # (manual)
	'Disease': 'Q12136',
	'LaunchPad': 'Q1353183',  # Q1353183 = "launch pad"  #####
	'River': 'Q4022',
	'Film': 'Q11424',
	'Spacecraft': 'Q40218',
	'Island': 'Q23442',
	'GolfPlayer': 'Q5',  # replaced automatic 'Q11303721' with 'Q5'
	'Region': 'Q3455524',
	'Broadcaster': 'Q15265344',
	'File': 'Q82753',  # Q82753 = "computer file"  #####
	'LegalCase': 'Q2334719',  # Q2334719 = "legal case"  #####
	'YearInSpaceflight': '',  # N/A
	'SportsEvent': 'Q16510064',  # Q16510064 = "sporting event" (or "sports event")  #####
	'Bridge': 'Q12280',
	'School': 'Q3914',
	'MilitaryAircraft': 'Q216916',  # Q216916 = "military aircraft"  #####
	'Food': 'Q2095',
	'ChristianDoctrine': 'Q3714546',  # Q3714546 = "Christian doctrine"  #####
	'MilitaryPerson': 'Q5',  # (manual)
	'TelevisionEpisode': 'Q21191270',  # Q21191270 = "television series episode" (or "television episode")  #####
	'Event': 'Q1656682',
	'Olympics': 'Q5389',  # Q5389 = "Olympic Games" (or "Olympics")  #####
	'Woman': 'Q5',  # (manual)
	'MilitaryUnit': 'Q176799',  # Q176799 = "military unit"  #####
	'Regency': 'Q173843',  # Q173843 = "regency"  #####
	'Boxer': 'Q5',  # (manual)
	'PoliticalParty': 'Q7278',  # Q7278 = "political party"  # (manual)  # Instance tested: Christian Democratic Union (Q49762) => political party in Germany (Q2023214) => political party (Q7278)  # Q7278.P1709 == "http://dbpedia.org/ontology/PoliticalParty"
	'Play': 'Q25379',
	'Airline': 'Q46970',
	'ChartsPlacements': '',  # N/A
	'MusicGenre': 'Q188451',  # Q188451 = "music genre"  # (manual)  # No instances tested but Q188451.P1709 == "http://dbpedia.org/ontology/MusicGenre"
	'ReligiousBuilding': 'Q24398318',  # Q24398318 = "religious building"  # (manual)  # Instances tested: Church of Our Lady (Q157229) => church building (Q16970) => religious building (Q24398318) ; Westminster Abbey (Q5933) => Anglican or episcopal cathedral (Q56242250) => protestant cathedral (Q58079064) => religious building (Q24398318)
	'AnatomicalStructure': 'Q4936952',  # Q4936952 = "anatomical structure"  # (manual)  # No instances tested but Q4936952.P1709 == "http://dbpedia.org/ontology/AnatomicalStructure"
	'TennisPlayer': 'Q5',  # (manual)
	'Airport': 'Q1248784',
	'Mountain': 'Q8502',
	'ArchitecturalStructure': 'Q811979',  # Q811979 = "architectural structure"  ##### 
	'GridironFootballPlayer': 'Q5',  # (manual)
	'Road': 'Q34442',
	'Work': 'Q386724',
	'MeanOfTransportation': 'Q29048322',  # Q29048322 = "vehicle model"  # (manual)  # Not based on any instances or any of the other main approaches; it's simply the superclass of automobile model (Q3231690), just like "MeanOfTransportation" is the superclass of "Automobile" in DBpedia!
	'Company': 'Q4830453',  # Q4830453 = "business"  # (manual)  # Note that Wikidata distinguishes between enterprise, business and corporation! Apple, Microsoft, Tesla and Unilever are all instances of "business" however (Unilever recursively via 1 step)!
	'Memorial': 'Q5003624',  # Q5003624 = "memorial"  # (manual)  # Instances tested: Lincoln Memorial (Q213559) => National Memorial of the United States (Q1967454) => memorial (Q5003624) ; Memorial to the Murdered Jews of Europe (Q160700) => Holocaust memorial (Q20011797) => war memorial (Q575759) => memorial (Q5003624)
	'Museum': 'Q33506',
	'Sales': 'Q194189',
	'Country': 'Q6256',
	'MilitaryConflict': 'Q198', # Q198 = "war" (or "military conflict")  #####
	'Artist': 'Q5',  # replaced automatic 'Q483501' with 'Q5'
	'Aircraft': 'Q11436',
	'Album': 'Q482994',
	'Saint': 'Q5',  # replaced automatic 'Q43115' with 'Q5'
	'AutomobileEngine': 'Q106708186',  # Q106708186 = "automobile engine"  # (manual)  # Could not find any instances but Q106708186 is a subclass of engine (Q44167)!
	'PowerStation': 'Q159719',  # Q159719 = "power station"  # (manual)  # No instances tested but Q159719.P1709 == "http://dbpedia.org/ontology/PowerStation"
	'Actor': 'Q5',  # replaced automatic 'Q33999' with 'Q5'
	'MusicalWork': 'Q105543609',  # Q105543609 = "musical work/composition"  # (manual)  # Instances tested: Billie Jean, Paradise City, We Will Rock You, Smells Like Teen Spirit ("Hot Stuff" doesn't work though!)
	'SoccerPlayer': 'Q5',  # (manual)
	'RouteOfTransportation': 'Q83620',  # Q83620 = "thoroughfare"  # (manual)  # Not instances tested and no P1709 property but in Wikidata thoroughfare (Q83620) is the superclass of road (Q34442) and bridge (Q12280); just like RouteOfTransportation is the superclass of Road and Bridge in DBpedia.
	'RomaniaSettlement': 'Q640364',  # Q640364 = "municipiu of Romania"  # (manual)  # Instances tested: Bucharest (Q19660) => municipiu of Romania (Q640364) ; Oradea (Q93358) => municipiu of Romania (Q640364)
	'Grape': 'Q10978',
	'Mill': 'Q44494',
	'AdministrativeRegion': 'Q56061', # Q56061 = "administrative territorial entity" (or "administrative region")  #####
	'CollegeCoach': 'Q5',  # (manual)
	'Project': 'Q170584',  # Q170584 = "Q170584"  # (manual)  # Not based on any instances but solely on a mapping provided by one of the other main approaches!!
	'ProtectedArea': 'Q473972',  # Q473972 = "protected area"  # (manual)  # No instances tested but Q473972.P1709 == "http://dbpedia.org/ontology/ProtectedArea"
	'Family': 'Q8436',
	'Openswarm': '',  # N/A (what is this?!)
	'Criminal': 'Q5',  # replaced automatic 'Q2159907' with 'Q5'
	'RadioStation': 'Q14350',  # Q14350 = "radio station"  # (manual)  # No instances and no P1709 property tested but radio station (Q14350) is subclass of broadcaster (Q15265344) and Q15265344.P1709 == "http://dbpedia.org/ontology/Broadcaster" (which is the superclass of RadioStation in DBpedia!)
	'CelestialBody': 'Q6999',  # Q6999 = "astronomical object"  # (manual)  # Instances tested: Jupiter (Q319), Milky Way (Q321)  # According to https://dbpedia.org/ontology/CelestialBody, both planets and galaxies are CelestialBodies in DBpedia.
	'IceHockeyPlayer': 'Q5',  # (manual)
	'Agent': 'Q24229398',
	'Statistic': 'Q1949963',
	'FormerMunicipality': 'Q19730508',  # Q19730508 = "former municipality" # (manual)  # No instances tested but Q19730508.P1709 == "http://dbpedia.org/ontology/FormerMunicipality"
	'Municipality': 'Q15284',  # Q15284 = "municipality"  # (manual)  # No instances tested and no P1709 property but it's the superclass of former municipality (Q19730508) for which Q19730508.P1709 == "http://dbpedia.org/ontology/FormerMunicipality" and Municipality is also the superclass of FormerMunicipality in DBpedia!
	'Organisation,_PopulatedPlace': '',  # N/A  # common attributes: ['dissolutionDate', 'dissolutionYear']
	'TelevisionShow': 'Q15416',  # Q15416 = "television program"  # (manual)  # No instances tested but Q15416.P1709 == "http://dbpedia.org/ontology/TelevisionShow"
	'Hotel': 'Q27686',
	'FictionalCharacter': 'Q95074',  # Q95074 = "fictional character"  # (manual)  # No instances tested but Q95074.P1709 == "http://dbpedia.org/ontology/FictionalCharacter"
	'Automobile': 'Q3231690',  # Q3231690 = "automobile model"  # (manual)  # Instances tested: Plymouth Satellite (Q1808628), Fiat Multipla (Q223621), Škoda Roomster (Q392071)  # Using `grep "<http://dbpedia.org/ontology/Automobile>" instance_types_en.ttl`, we can see that DBpedia means automobile *model* with "Automobile".
	'NorwaySettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'Scientist': 'Q5',  # replaced automatic 'Q901' with 'Q5'
	'FigureSkater': 'Q5',  # (manual)
	'Animal': 'Q729',
	'Infrastructure': 'Q121359',  # Q121359 = "infrastructure"  #####
	'Cemetery': 'Q39614',
	'HistoricPlace': 'Q1081138',  # Q1081138 = "historic site" (or "historic place")  #####
	'SnookerPlayer': 'Q5',  # (manual)
	'Race': 'Q878123',  # Q878123 = "racing" (or "race")  #####
	'Instrument': 'Q34379',  # Q34379 = "musical instrument" (description of Instrument in DBpedia = "Describes all musical instrument")  #####
	'Language': 'Q34770',  # 2 candidates: 'Q315' and 'Q34770'
	'Galaxy': 'Q318',
	'Constellation': 'Q8928',
	'SoccerLeagueSeason': 'Q27020041',  # Q27020041 = "sports season"  # (manual)  # Instance tested: 2022 Canadian Soccer League season (Q111837327) => sports season (Q27020041)
	'BaseballPlayer': 'Q5',  # (manual)
	'Ship': 'Q11446',  # Q11446 = "ship"  # (manual)  # Instances tested: Titanic (Q25173) => steamship (Q12859788) => ship (Q11446) ; USS Gerald R. Ford (Q1351895) => supercarrier (Q1186981) => aircraft carrier (Q17205) => warship (Q3114762) => naval vessel (Q177597) => ship (Q11446)
	'Opera': 'Q1344',
	'Letter': 'Q9788',  # 2 candidates: 'Q133492' (msg) and 'Q9788' (grapheme)
	'Brain': 'Q1073',  # Q1073 = "brain"  #####
	'ChemicalElement': 'Q11344',  # Q11344 = "chemical element"  # (manual)  # Instances tested: bromine (Q879), potassium (Q703)
	'StatedResolution': '',  # N/A
	'PersonFunction': '',  # N/A
	'Weapon': 'Q728',
	'ConcentrationCamp': 'Q152081',  # Q152081 = "concentration camp"  # (manual)  # Instance tested: Auschwitz (Q7341) => Nazi concentration camp (Q328468) => concentration camp (Q152081)
	'RecordLabel': 'Q18127',  # Q18127 = "record label"  # (manual)  # No instances tested but Q18127.P1709 == "http://dbpedia.org/ontology/RecordLabel"
	'Cartoon': 'Q627603',
	'EducationalInstitution': 'Q2385804',  # Q2385804 = "educational institution"  #####
	'WineRegion': 'Q2140699',  # Q2140699 = "wine-producing region" (or "wine region")  #####
	'Protein': 'Q8054',
	'Shrine': 'Q697295',
	'UndergroundJournal': '',  # N/A
	'SpaceShuttle': 'Q48806',  # Q48806 = "Space Shuttle"  # (manual)  # No instances tested but Q48806.P1709 == "http://dbpedia.org/ontology/SpaceShuttle"
	'Hospital': 'Q16917',
	'University': 'Q3918',
	'AcademicJournal': 'Q737498',  # Q737498 = "academic journal"  # (manual)  # No instances tested but Q737498.P1709 == "http://dbpedia.org/ontology/AcademicJournal"
	'Beverage': 'Q40050',  # Q40050 = "drink" (or "beverage")  # (manual)  # Instances tested (actually subclasses!): absinthe (Q170210) => anise drink (Q549301) => spirit drink (Q17562878) => alcoholic beverage (Q154) => drink (Q40050) ; orange juice (Q219059) => fruit juice (Q20932605) => juice (Q8492) => drink (Q40050)
	'PublicTransitSystem': '',  # N/A
	'Man': 'Q5',  # (manual)
	'Building': 'Q41176',
	'MemberResistanceMovement': 'Q5',  # (manual)
	'SportsTeam': 'Q12973014',  # Q12973014 = "sports team"  # (manual)  # Both Wikidata and DBpedia differentiate between SportsTeam and SportsClub, a common superclass would be Q4438121 (sports organization) or "Organization" in DBpedia!
	'ResearchProject': 'Q1298668',
	'Architect': 'Q5',  # (manual)
	'Currency': 'Q8142',  # Q8142 = "currency"  # (manual)  # Instances tested: euro (Q4916), Argentine peso (Q199578)
	'SportCompetitionResult': '',  # N/A
	'Blazon': 'Q14659',  # Q14659 = "coat of arms" (both "coat of arms" and "blazon" tranlate to "Wappen" in German)  #####
	'Software': 'Q7397',
	'PeriodicalLiterature': 'Q1002697',  # Q1002697 = "periodical" (or "periodical literature")  # (manual)  # No instances tested but Q1002697.P1709 == "http://dbpedia.org/ontology/PeriodicalLiterature"
	'LawFirm': 'Q613142',  # Q613142 = "law firm"  # (manual)  # No instances tested but Q613142.P1709 == "http://dbpedia.org/ontology/LawFirm"
	'Rocket': 'Q41291',
	'ChemicalSubstance': 'Q79529',  # Q79529 = "chemical substance"  #####
	'SoccerClub': 'Q476028',  # Q476028 = "association football club"  # (manual)  # Instances tested: FC Bayern Munich (Q15789), Real Madrid CF (Q8682)
	'Attack': 'Q2223653',  # Q2223653 = "terrorist attack"  #####
	'Activity': 'Q1914636',
	'Biomolecule': 'Q206229',
	'Horse': 'Q726',  # Q726 = "horse"  #####
	'Outbreak': 'Q3241045',  # Q3241045 = "disease outbreak" (or "outbreak")  #####
	'Single': 'Q134556',
	'Song': 'Q2188189', # Q2188189 = "musical work"  #####
	'Writer': 'Q5',  # replaced automatic 'Q36180' with 'Q5'
	'company': 'Q4830453',  # For some reasons there also exists a lower-case version of "Company", map it to the same Wikidata Item of course!  # (manual)
	'Artwork': 'Q17537576', # There are 2 candiates: work of art (Q838948) & creative work (or "work of art") (Q17537576) (superclass of Q838948)  #####
	'SkiArea': 'Q3034650',  # Q3034650 = "ski area"  #####
	'ChessPlayer': 'Q5',  # (manual)
	'College': 'Q189004',  # Q189004 = "college" (higher education institution)  #####
	'Globularswarm': '',  # N/A  # What is this?!
	'Cricketer': 'Q5',  # (manual)
	'OlympicResult': '',  # N/A
	'GermanSettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'Document': 'Q49848',  # Q49848 = "document"  #####
	'RestArea': 'Q786014',  # Q786014 = "rest area"  #####
	'Band': 'Q215380',
	'Athlete,_CareerStation': '',  # N/A  # common attributes: ['amateurYear', 'amateurTeam', 'leadTeam', 'cyclistGenre', 'leadYear', 'proTeam']
	'SoccerTournament': '',  # N/A
	'ShoppingMall': 'Q31374404',
	'Magazine': 'Q41298',
	'SportsLeague': 'Q623109',  # Q623109 = "sports league"  # (manual)  # No instances tested but Q623109.P1709 == "http://dbpedia.org/ontology/SportsLeague"
	'Library': 'Q7075',
	'HungarySettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'GeneLocation': 'Q106227',  # Q106227 = "locus" (or "genetic location")  #####
	'Cleric': 'Q5',  # (manual)
	'TermOfOffice': 'Q524572',  # Q524572 = "term of office"  # (manual)  # No instances tested but Q524572.P1709 == "http://dbpedia.org/ontology/TermOfOffice"
	'Train': 'Q870',
	'Colour': 'Q1075',  # Q1075 = "color"  # (manual)  # Instances tested: red (Q3142), blue (Q1088)
	'BelgiumSettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'Sport': 'Q349',
	'Stream': 'Q47521',
	'FilmFestival': 'Q220505',
	'Nerve': 'Q9620',
	'Case': '',  # N/A
	'PenaltyShootOut': 'Q2691960',  # Q2691960 = "penalty shoot-out" (method used in association football to decide the winner of a drawn match)  # chosen because German translation of PenaltyShootOut DBpedia class is "Elfmeterschiessen"  #####
	'Royalty': '',  # N/A  # Q3446302 = "royalty" (type of political organisation) best matches but it's not a subclass of anything!!! ; other candidates were Q11573099 (royalty; family and relative members of a soverign) and Q2006518 (royal family; family of a monarch) but Q3446302 (royalty; type of political organisation) best matches DBpedia's "Royalty" class whose name is tranlated as "Koenigtum" into German
	'NobleFamily': 'Q13417114',  # Q13417114 = "noble family"  # (manual)  # No instances tested but Q13417114.P1709 == "http://dbpedia.org/ontology/NobleFamily"
	'LiechtensteinSettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'Skyscraper': 'Q11303',
	'WikimediaTemplate': 'Q11266439',  # Q11266439 = "Wikimedia template"  #####
	'Newspaper': 'Q11032',
	'FormulaOneRacing': 'Q2705092',  # Q2705092 = "Formula One racing"  #####
	'ArchitecturalStructure,_Monument': '',  # N/A  # common attributes: ['dutchMIPCode']
	'EthnicGroup': 'Q41710',  # Q41710 = "ethnic group"  # (manual)  # No instances tested but Q41710.P1709 == "http://dbpedia.org/ontology/EthnicGroup"
	'Monument': 'Q4989906',
	'WrestlingEvent': 'Q21156425',  # Q21156425 = "wrestling event" ; a subclass of Q21156425 is: professional wrestling event (Q17317604)  #####
	'SiteOfSpecialScientificInterest': '',  # N/A
	'MultiVolumePublication': '',  # N/A
	'MythologicalFigure': 'Q4271324',  # Q4271324 = "mythical character" (or "mythological figure")  # (manual)  # Instances tested: Thor (Q42952) => Norse deity (Q16513881) => Norse mythical character (Q16513904) => mythical character (Q4271324) ; Poseidon (Q41127) => Greek deity (Q22989102) => mythological Greek character (Q22988604) => mythical character (Q4271324)  # Q4271324.P1709 == "http://dbpedia.org/ontology/MythologicalFigure"
	'Flag': 'Q14660',
	'RouteStop': 'Q548662',  # Q548662 = "public transport stop"  #####
	'Restaurant': 'Q11707',
	'BodyOfWater': 'Q15324',  # Q15324 = "body of water"  # (manual)  # Instances tested:  Lake Huron (Q1383) => lake (Q23397) => body of water (Q15324) ; Caspian Sea (Q5484) => body of water (Q15324)
	'SubMunicipality': 'Q15284',  # Simply mapped to the same Wikidata item as "Municipality" ; note that "SubMunicipality" is NOT a subclass of "Municipality" in DBpedia though!!! (they are both subclasses of "GovernmentalAdministrativeRegion")  #####
	'Drug': 'Q8386',
	'RaceTrack': 'Q1777138',  # Q1777138 = "race track"  # Q1777138.P1709 == "http://dbpedia.org/ontology/Racecourse" which is a SUBCLASS of RaceTrack!  #####
	'Locomotive': 'Q93301',
	'CareerStation': '',  # N/A
	'Theatre': 'Q24354',
	'Monastry': '',  # N/A  # What is this?!  # Do they mean "monastery" ?!
	'Plant': 'Q756',
	'MilitaryConflict_,_NaturalEvent_,_Attack': '',  # N/A  # common attributes: ['casualties']
	'VolleyballPlayer': 'Q5',  # (manual)
	'AdultActor': 'Q5',  # (manual)
	'Organisation,_Parish': '',  # N/A
	'WorldHeritageSite': '',  # N/A  # There appears to be no Wikidata class for this, at least when looking at Acropolis of Athens (Q131013) and Temples of Abu Simbel (Q134140).
	'City': 'Q515',
	'Wrestler': 'Q5',  # replaced automatic 'Q13474373' with 'Q5'
	'core#Concept': '',  # N/A  # Better not match this to any equivalent thing in Wikidata because it is TOO generic!!!
	'MountainRange': 'Q46831',  # Q46831 = "mountain range"  # (manual)  # No instances tested but Q46831.P1709 == "http://dbpedia.org/ontology/MountainRange"
	'OfficeHolder': 'Q5',  # (manual)
	'Diocese,_Parish': '',  # N/A  # common attributes: ['deanery']
	'Monarch': 'Q5',  # replaced automatic 'Q116' with 'Q5'
	'MilitaryConflict,_AdministrativeRegion': '',  # N/A  # common attributes: ['territory']
	'ChemicalCompound': 'Q11173',  # Q11173 = "chemical compound"  # (manual)  # No instances tested but Q11173.P1709 == "http://dbpedia.org/ontology/ChemicalCompound"
	'MusicalArtist': 'Q5',  # (manual)
	'TelevisionStation': 'Q1616075',  # Q1616075 = "television station" (is also a subclass of broadcaster (Q15265344) which has P1709 == "http://dbpedia.org/ontology/Broadcaster")  # (manual)  # cf. "RadioStation", it's the same there!
	'Law': 'Q820655',  # Q820655 = "statute" (both Wikidata's "statue" and DBpedia's "Law" are translated into German as "Gesetz")  # (manual)  # Derived from these two instances: Civil Rights Act of 1964 (Q585962) => Act of Congress in the United States (Q476068) => federal law (Q1006612) => statute (Q820655) ; transgender rights in Germany / Transsexuellengesetz (Q1777996) => federal act (Q1006079) =>  federal law (Q1006612) => statute (Q820655)
	'Astronaut': 'Q5',  # replaced automatic 'Q11631' with 'Q5'
	'Continent': 'Q5107',  # Q5107 = "continent"  # (manual)  # Instances tested: Europe (Q46), Asia (Q48), Africa (Q15)
	'Lake': 'Q23397',
	'Volcano': 'Q8072',
	'SwitzerlandSettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'Swimmer': 'Q5',  # replaced automatic 'Q10843402' with 'Q5'
	'WaterwayTunnel': 'Q811979',  # is a subclass of "ArchitecturalStructure" in DBpedia, which we mapped to "Q811979" (see above)  #####
	'Mayor': 'Q5',  # replaced automatic 'Q30185' with 'Q5'
	'SupremeCourtOfTheUnitedStatesCase': 'Q19692072',  # Q19692072 = "United States Supreme Court decision" (a subclass of legal case (Q2334719))  # An instance is Reynolds v. United States (Q7319687) for example, although that one was only found via search for "Supreme Court Of The United States Case" so it's not representative for possible other Wikidata items that might be an instance of Q19692072...!  #####
	'Coach': 'Q5',  # (manual)
	'LebanonSettlement': 'Q486972',  # (manual)  # Simply mapped to the same WikidataItem as its superclass "Settlement".
	'SportsTeamMember': 'Q5',  # (manual)
	'NuclearPowerStation': 'Q134447',  # Q134447 = "nuclear power plant"  # (manual)  # No instances tested but Q134447.P1709 == "http://dbpedia.org/ontology/NuclearPowerStation"
	'Bishop': 'Q5',  # (manual)
	'District': 'Q149621',  # Q149621 = "district"  # Q149621 is a subclass of administrative territorial entity (Q56061), which we mapped to "AdministrativeRegion", which is also the superclass of "District" in DBpedia, so that fits!!  #####
	'TimePeriod': 'Q186081',  # Q186081 = "time interval" (or "time period"), which is a superclass of historical period (Q11514315) which corresponds to http://dbpedia.org/ontology/HistoricalPeriod according to the P1709 property and HistoricalPeriod is also a subclass of TimePeriod in DBpedia, so that fits!!  #####
	'Election': 'Q40231',
	'VideoGame': 'Q7889',
	'Mountain,Volcano': '',  # N/A  # common attributes: ['firstAscent']
	'Painting': 'Q3305213',  # Q3305213 = "painting"  # (manual)  # Instances tested: Mona Lisa (Q12418) => painting (Q3305213) ; American Gothic (Q464782) => painting (Q3305213)
	'Intercommunality': 'Q3153117',
	'MilitaryConflict_,_Attack': '',  # N/A  # common attributes: ['weapon']
	'Artery': 'Q9655',  # Q9655 = "artery" (the blood vessel that...)  #####
	'Gene': 'Q7187',
	'GraveMonument': 'Q56055312',  # Q56055312 = "sepulchral monument" (structures marking or denoting burial sites, also "grave monument")  #####
	'Organization': 'Q43229',  # Q43229 = "organization"  # (manual)  # Instances tested: NATO (Q7184), FAO (Q82151); business (Q4830453) is also a subclass of Q43229!
	'CyclingTeam': 'Q1785271',  # Q1785271 = "cycling team"  #####
	'PoliticalFunction': '',  # N/A
	'Musical': 'Q2743',
	'Priest': 'Q5',  # replaced automatic 'Q42603' with 'Q5'
	'Muscle': 'Q7365',
	'RoadJunction': 'Q1788454',  # Q1788454 = "road junction"  #####
	'Cave': 'Q35509',
	'Politician': 'Q5',  # replaced automatic 'Q82955' with 'Q5'
	'NationalCollegiateAthleticAssociationAthlete': 'Q5',  # (manual)
	'SingleList': '',  # N/A
	'GivenName': 'Q202444',  # Q202444 = "given name"  # (manual)  # No instances tested but Q202444.P1709 == "http://dbpedia.org/ontology/GivenName"
	'ClericalAdministrativeRegion': 'Q56061',  # Simply mapped to the same Wikidata item as the subclass "AdministrativeRegion"  #####
	'CityDistrict': 'Q4286337',  # Q4286337 = "city district" (type of administrative division), which is a subclass of district (Q149621), which we mapped to "District", so that fits!!  #####
	'SpaceStation': 'Q25956',  # Q25956 = "space station"  # (manual)  # No instances tested but Q25956.P1709 == "http://dbpedia.org/ontology/SpaceStation"
	'Engine': 'Q44167',  # Q44167 = "engine"  # (manual)  # Could not find any instances but Q44167 does have a subclass-of property!
	'HistoricBuilding': 'Q35112127',  # Q35112127 = "historic building" (structure of historic nature)  #####
	'RailwayTunnel': 'Q1311958',  # Q1311958 = "railway tunnel"  # (manual)  # No instances tested but Q1311958.P1709 == "http://dbpedia.org/ontology/RailwayTunnel"
	'GolfCourse': 'Q1048525',  # Q1048525 = "golf course"  # (manual)  # No instances tested but Q1048525.P1709 == "http://dbpedia.org/ontology/GolfCourse"
	'On-SiteTransportation': '',  # N/A  # Note: In DBpedia, On-SiteTransportation is the superclass of: ConveyorSystem, Escalator, MovingWalkway!
	'Escalator': 'Q15003',  # Q15003 = "escalator" (moving staircase)  #####
	'ConveyorSystem': 'Q577998',  # Q577998 = "conveyor system" (equipment used for conveying materials)  #####
	'MovingWalkway': 'Q847580',  # Q847580 = "moving walkway" (roughly horizontal conveyor for pedestrians)  #####
	'GeopoliticalOrganisation': 'Q43229',  # Simply using the same mapping as for 'Organization' here.  # (manual)
	'LunarCrater': 'Q55818',  # Q55818 = "impact crater"  # (manual)  # Of Webb (Q1131919), Moltke (Q620980), Eratosthenes (Q1345034) and Copernicus (Q1131154), only Moltke is an instance of the more specific lunar crater (Q1348589) class!
}


def get_dbpedia_classes_mapped_to_wikidata() -> Dict[str, str]:
 	return dbpediaClassesMappedToWikidata


def main():
	RAWdbpediaClassesMappedToWikidata: Dict[str, str] = {}
	# Not to be confused with the manually curated (and static)
	#   `dbpediaClassesMappedToWikidata` above!
	# This main() exists to create a skelton dictionary that takes less time
	#   to complete manually than to create one from scratch, manually.

	# (1) Extract all DBpedia classes from .owl file:

	dbpediaClassesToProperties: Dict[str, List[str]] = get_dbpedia_properties()

	dbpediaClassNames: List[str] = list(dbpediaClassesToProperties.keys())

	# Initialize RAWdbpediaClassesMappedToWikidata with the keys already:
	for dbpedia_class_name in dbpediaClassNames:
		RAWdbpediaClassesMappedToWikidata[dbpedia_class_name] = ""

	# (2) Search Wikidata for every DBpedia class name.
	#     Hopefully, one of the search results will have the
	#     P1709 (equivalent class) property defined, containing the
	#     equivalent DBpedia class:

	for dbpedia_class_name in dbpediaClassNames:
		matching_wikidata_items: List[WikidataItem] =\
			WikidataItem.get_items_matching_search_string(\
				search_string=dbpedia_class_name)
		
		for matching_wikidata_item in matching_wikidata_items:
			equivalent_classes: List[str] =\
				matching_wikidata_item.get_property("P1709")
			if equivalent_classes is not None and equivalent_classes != []:
				print("[INFO] Found equivalent classes for Wikidata " +\
					f"item/class '{matching_wikidata_item}' " +\
					"(found by searching "+\
					f"for DBpedia class name '{dbpedia_class_name}'): " +\
					f"{equivalent_classes}")
				for equivalent_class in equivalent_classes:
					if equivalent_class\
						== "http://dbpedia.org/ontology/" + dbpedia_class_name:
					    # e.g. WikidataItem("Q937857").get_property("P1709")
					    #      == ['http://dbpedia.org/ontology/SoccerPlayer']
					    #
					    # Important note: we have to insist on strict equality
					    # here. Otherwise DBpedia's "Engine" will be mapped to
					    # Wikidata's https://www.wikidata.org/wiki/Q81096
					    # (engineer)!
						RAWdbpediaClassesMappedToWikidata[dbpedia_class_name]+=\
							matching_wikidata_item.entity_id
						print(f"[Info] Mapped '{dbpedia_class_name}' => " +\
							f"'{matching_wikidata_item.entity_id}'")
		
		if RAWdbpediaClassesMappedToWikidata[dbpedia_class_name] == "":
			print(f"[INFO] No equivalent Wikidata item/class found for " +\
				f"DBpedia class '{dbpedia_class_name}'")

	# (3) Print result:

	print(\
		str(len(\
			list(filter(lambda v: v != "",\
				RAWdbpediaClassesMappedToWikidata.values()))
		)) +\
		" out of " + str(len(RAWdbpediaClassesMappedToWikidata)) +\
		" DBpedia classes mapped to Wikidata entries:"\
		)
	print("")
	print("{")
	for key, value in RAWdbpediaClassesMappedToWikidata.items():
		print(f"\t'{key}': '{value}',")
	print("}")
	# print(RAWdbpediaClassesMappedToWikidata) #...is without linebreaks!


if __name__ == "__main__":
	main()
