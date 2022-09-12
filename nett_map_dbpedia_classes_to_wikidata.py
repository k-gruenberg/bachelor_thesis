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
#                       -  27 further manual mappings
#                       - 130 DBpedia classes w/o Wikidata mappings (45.9%)
#                   SUM = 283 DBpedia classes
dbpediaClassesMappedToWikidata: Dict[str, str] =\
{
	'Legislature': 'Q11204',
	'GrandPrix': '',
	'Athlete': 'Q5',  # (manual)
	'Person': 'Q5',  # replaced automatic 'Q215627' with 'Q5'
	'Settlement': 'Q486972',
	'PopulatedPlace': 'Q486972',  # Q486972 = "human settlement"  # (manual)
	'SpaceMission': 'Q2133344',  # Q2133344 = "space mission"  # (manual)  # Instance tested: Apollo 13 (Q182252) => human spaceflight (Q752783) => space mission (Q2133344)  # Q2133344.P1709 == "http://dbpedia.org/ontology/SpaceMission"
	'Organisation': 'Q43229',
	'Species': '',
	'Place': 'Q17334923',
	'Station': 'Q12819564',
	'FormulaOneRacer': 'Q5',  # (manual)
	'Planet': 'Q634',
	'PokerPlayer': 'Q5',  # (manual)
	'WrittenWork': 'Q47461344',  # Q47461344 = "written work"  # (manual)
	'Department': '',
	'Canal': 'Q12284',  # Q12284 = "canal"  # (manual)  # Instances tested: Erie Canal (Q459578) => canal (Q12284) ; Mittelland Canal (Q48480) => summit level canal (Q2936105) => canal (Q12284)
	'Reference': '',
	'SkiResort': '',
	'Comedian': 'Q5',  # (manual)
	'Disease': 'Q12136',
	'LaunchPad': '',
	'River': 'Q4022',
	'Film': 'Q11424',
	'Spacecraft': 'Q40218',
	'Island': 'Q23442',
	'GolfPlayer': 'Q5',  # replaced automatic 'Q11303721' with 'Q5'
	'Region': 'Q3455524',
	'Broadcaster': 'Q15265344',
	'File': '',
	'LegalCase': '',
	'YearInSpaceflight': '',
	'SportsEvent': '',
	'Bridge': 'Q12280',
	'School': 'Q3914',
	'MilitaryAircraft': '',
	'Food': 'Q2095',
	'ChristianDoctrine': '',
	'MilitaryPerson': 'Q5',  # (manual)
	'TelevisionEpisode': '',
	'Event': 'Q1656682',
	'Olympics': '',
	'Woman': 'Q5',  # (manual)
	'MilitaryUnit': '',
	'Regency': '',
	'Boxer': 'Q5',  # (manual)
	'PoliticalParty': '',
	'Play': 'Q25379',
	'Airline': 'Q46970',
	'ChartsPlacements': '',
	'MusicGenre': '',
	'ReligiousBuilding': 'Q24398318',  # Q24398318 = "religious building"  # (manual)  # Instances tested: Church of Our Lady (Q157229) => church building (Q16970) => religious building (Q24398318) ; Westminster Abbey (Q5933) => Anglican or episcopal cathedral (Q56242250) => protestant cathedral (Q58079064) => religious building (Q24398318)
	'AnatomicalStructure': '',
	'TennisPlayer': 'Q5',  # (manual)
	'Airport': 'Q1248784',
	'Mountain': 'Q8502',
	'ArchitecturalStructure': '',
	'GridironFootballPlayer': 'Q5',  # (manual)
	'Road': 'Q34442',
	'Work': 'Q386724',
	'MeanOfTransportation': 'Q29048322',  # Q29048322 = "vehicle model"  # (manual)  # Not based on any instances or any of the other main approaches; it's simply the superclass of automobile model (Q3231690), just like "MeanOfTransportation" is the superclass of "Automobile" in DBpedia!
	'Company': 'Q4830453',  # Q4830453 = "business"  # (manual)  # Note that Wikidata distinguishes between enterprise, business and corporation! Apple, Microsoft, Tesla and Unilever are all instances of "business" however (Unilever recursively via 1 step)!
	'Memorial': 'Q5003624',  # Q5003624 = "memorial"  # (manual)  # Instances tested: Lincoln Memorial (Q213559) => National Memorial of the United States (Q1967454) => memorial (Q5003624) ; Memorial to the Murdered Jews of Europe (Q160700) => Holocaust memorial (Q20011797) => war memorial (Q575759) => memorial (Q5003624)
	'Museum': 'Q33506',
	'Sales': 'Q194189',
	'Country': 'Q6256',
	'MilitaryConflict': '',
	'Artist': 'Q5',  # replaced automatic 'Q483501' with 'Q5'
	'Aircraft': 'Q11436',
	'Album': 'Q482994',
	'Saint': 'Q5',  # replaced automatic 'Q43115' with 'Q5'
	'AutomobileEngine': 'Q106708186',  # Q106708186 = "automobile engine"  # (manual)  # Could not find any instances but Q106708186 is a subclass of engine (Q44167)!
	'PowerStation': '',
	'Actor': 'Q5',  # replaced automatic 'Q33999' with 'Q5'
	'MusicalWork': 'Q105543609',  # Q105543609 = "musical work/composition"  # (manual)  # Instances tested: Billie Jean, Paradise City, We Will Rock You, Smells Like Teen Spirit ("Hot Stuff" doesn't work though!)
	'SoccerPlayer': 'Q5',  # (manual)
	'RouteOfTransportation': '',
	'RomaniaSettlement': '',
	'Grape': 'Q10978',
	'Mill': 'Q44494',
	'AdministrativeRegion': '',
	'CollegeCoach': 'Q5',  # (manual)
	'Project': 'Q170584',  # Q170584 = "Q170584"  # (manual)  # Not based on any instances but solely on a mapping provided by one of the other main approaches!!
	'ProtectedArea': '',
	'Family': 'Q8436',
	'Openswarm': '',
	'Criminal': 'Q5',  # replaced automatic 'Q2159907' with 'Q5'
	'RadioStation': '',
	'CelestialBody': 'Q6999',  # Q6999 = "astronomical object"  # (manual)  # Instances tested: Jupiter (Q319), Milky Way (Q321)  # According to https://dbpedia.org/ontology/CelestialBody, both planets and galaxies are CelestialBodies in DBpedia.
	'IceHockeyPlayer': 'Q5',  # (manual)
	'Agent': 'Q24229398',
	'Statistic': 'Q1949963',
	'FormerMunicipality': '',
	'Municipality': '',
	'Organisation,_PopulatedPlace': '',  # common attributes: ['dissolutionDate', 'dissolutionYear']
	'TelevisionShow': '',
	'Hotel': 'Q27686',
	'FictionalCharacter': '',
	'Automobile': 'Q3231690',  # Q3231690 = "automobile model"  # (manual)  # Instances tested: Plymouth Satellite (Q1808628), Fiat Multipla (Q223621), Škoda Roomster (Q392071)  # Using `grep "<http://dbpedia.org/ontology/Automobile>" instance_types_en.ttl`, we can see that DBpedia means automobile *model* with "Automobile".
	'NorwaySettlement': '',
	'Scientist': 'Q5',  # replaced automatic 'Q901' with 'Q5'
	'FigureSkater': 'Q5',  # (manual)
	'Animal': 'Q729',
	'Infrastructure': '',
	'Cemetery': 'Q39614',
	'HistoricPlace': '',
	'SnookerPlayer': 'Q5',  # (manual)
	'Race': '',
	'Instrument': '',
	'Language': 'Q34770',  # 2 candidates: 'Q315' and 'Q34770'
	'Galaxy': 'Q318',
	'Constellation': 'Q8928',
	'SoccerLeagueSeason': '',
	'BaseballPlayer': 'Q5',  # (manual)
	'Ship': 'Q11446',  # Q11446 = "ship"  # (manual)  # Instances tested: Titanic (Q25173) => steamship (Q12859788) => ship (Q11446) ; USS Gerald R. Ford (Q1351895) => supercarrier (Q1186981) => aircraft carrier (Q17205) => warship (Q3114762) => naval vessel (Q177597) => ship (Q11446)
	'Opera': 'Q1344',
	'Letter': 'Q9788',  # 2 candidates: 'Q133492' (msg) and 'Q9788' (grapheme)
	'Brain': '',
	'ChemicalElement': 'Q11344',  # Q11344 = "chemical element"  # (manual)  # Instances tested: bromine (Q879), potassium (Q703)
	'StatedResolution': '',
	'PersonFunction': '',
	'Weapon': 'Q728',
	'ConcentrationCamp': '',
	'RecordLabel': '',
	'Cartoon': 'Q627603',
	'EducationalInstitution': '',
	'WineRegion': '',
	'Protein': 'Q8054',
	'Shrine': 'Q697295',
	'UndergroundJournal': '',
	'SpaceShuttle': '',
	'Hospital': 'Q16917',
	'University': 'Q3918',
	'AcademicJournal': '',
	'Beverage': '',
	'PublicTransitSystem': '',
	'Man': 'Q5',  # (manual)
	'Building': 'Q41176',
	'MemberResistanceMovement': 'Q5',  # (manual)
	'SportsTeam': 'Q12973014',  # Q12973014 = "sports team"  # (manual)  # Both Wikidata and DBpedia differentiate between SportsTeam and SportsClub, a common superclass would be Q4438121 (sports organization) or "Organization" in DBpedia!
	'ResearchProject': 'Q1298668',
	'Architect': 'Q5',  # (manual)
	'Currency': 'Q8142',  # Q8142 = "currency"  # (manual)  # Instances tested: euro (Q4916), Argentine peso (Q199578)
	'SportCompetitionResult': '',
	'Blazon': '',
	'Software': 'Q7397',
	'PeriodicalLiterature': '',
	'LawFirm': '',
	'Rocket': 'Q41291',
	'ChemicalSubstance': '',
	'SoccerClub': 'Q476028',  # Q476028 = "association football club"  # (manual)  # Instances tested: FC Bayern Munich (Q15789), Real Madrid CF (Q8682)
	'Attack': '',
	'Activity': 'Q1914636',
	'Biomolecule': 'Q206229',
	'Horse': '',
	'Outbreak': '',
	'Single': 'Q134556',
	'Song': '',
	'Writer': 'Q5',  # replaced automatic 'Q36180' with 'Q5'
	'company': '',
	'Artwork': '',
	'SkiArea': '',
	'ChessPlayer': 'Q5',  # (manual)
	'College': '',
	'Globularswarm': '',
	'Cricketer': 'Q5',  # (manual)
	'OlympicResult': '',
	'GermanSettlement': '',
	'Document': '',
	'RestArea': '',
	'Band': 'Q215380',
	'Athlete,_CareerStation': '',  # common attributes: ['amateurYear', 'amateurTeam', 'leadTeam', 'cyclistGenre', 'leadYear', 'proTeam']
	'SoccerTournament': '',
	'ShoppingMall': 'Q31374404',
	'Magazine': 'Q41298',
	'SportsLeague': '',
	'Library': 'Q7075',
	'HungarySettlement': '',
	'GeneLocation': '',
	'Cleric': 'Q5',  # (manual)
	'TermOfOffice': '',
	'Train': 'Q870',
	'Colour': 'Q1075',  # Q1075 = "color"  # (manual)  # Instances tested: red (Q3142), blue (Q1088)
	'BelgiumSettlement': '',
	'Sport': 'Q349',
	'Stream': 'Q47521',
	'FilmFestival': 'Q220505',
	'Nerve': 'Q9620',
	'Case': '',
	'PenaltyShootOut': '',
	'Royalty': '',
	'NobleFamily': '',
	'LiechtensteinSettlement': '',
	'Skyscraper': 'Q11303',
	'WikimediaTemplate': '',
	'Newspaper': 'Q11032',
	'FormulaOneRacing': '',
	'ArchitecturalStructure,_Monument': '',
	'EthnicGroup': '',
	'Monument': 'Q4989906',
	'WrestlingEvent': '',
	'SiteOfSpecialScientificInterest': '',
	'MultiVolumePublication': '',
	'MythologicalFigure': 'Q4271324',  # Q4271324 = "mythical character" (or "mythological figure")  # (manual)  # Instances tested: Thor (Q42952) => Norse deity (Q16513881) => Norse mythical character (Q16513904) => mythical character (Q4271324) ; Poseidon (Q41127) => Greek deity (Q22989102) => mythological Greek character (Q22988604) => mythical character (Q4271324)  # Q4271324.P1709 == "http://dbpedia.org/ontology/MythologicalFigure"
	'Flag': 'Q14660',
	'RouteStop': '',
	'Restaurant': 'Q11707',
	'BodyOfWater': 'Q15324',  # Q15324 = "body of water"  # (manual)  # Instances tested:  Lake Huron (Q1383) => lake (Q23397) => body of water (Q15324) ; Caspian Sea (Q5484) => body of water (Q15324)
	'SubMunicipality': '',
	'Drug': 'Q8386',
	'RaceTrack': '',
	'Locomotive': 'Q93301',
	'CareerStation': '',
	'Theatre': 'Q24354',
	'Monastry': '',
	'Plant': 'Q756',
	'MilitaryConflict_,_NaturalEvent_,_Attack': '',  # common attributes: ['casualties']
	'VolleyballPlayer': 'Q5',  # (manual)
	'AdultActor': 'Q5',  # (manual)
	'Organisation,_Parish': '',
	'WorldHeritageSite': '',  # There appears to be no Wikidata class for this, at least when looking at Acropolis of Athens (Q131013) and Temples of Abu Simbel (Q134140).
	'City': 'Q515',
	'Wrestler': 'Q5',  # replaced automatic 'Q13474373' with 'Q5'
	'core#Concept': '',
	'MountainRange': '',
	'OfficeHolder': 'Q5',  # (manual)
	'Diocese,_Parish': '',
	'Monarch': 'Q5',  # replaced automatic 'Q116' with 'Q5'
	'MilitaryConflict,_AdministrativeRegion': '',  # common attributes: ['territory']
	'ChemicalCompound': '',
	'MusicalArtist': 'Q5',  # (manual)
	'TelevisionStation': '',
	'Law': 'Q820655',  # Q820655 = "statute" (both Wikidata's "statue" and DBpedia's "Law" are translated into German as "Gesetz")  # (manual)  # Derived from these two instances: Civil Rights Act of 1964 (Q585962) => Act of Congress in the United States (Q476068) => federal law (Q1006612) => statute (Q820655) ; transgender rights in Germany / Transsexuellengesetz (Q1777996) => federal act (Q1006079) =>  federal law (Q1006612) => statute (Q820655)
	'Astronaut': 'Q5',  # replaced automatic 'Q11631' with 'Q5'
	'Continent': 'Q5107',  # Q5107 = "continent"  # (manual)  # Instances tested: Europe (Q46), Asia (Q48), Africa (Q15)
	'Lake': 'Q23397',
	'Volcano': 'Q8072',
	'SwitzerlandSettlement': '',
	'Swimmer': 'Q5',  # replaced automatic 'Q10843402' with 'Q5'
	'WaterwayTunnel': '',
	'Mayor': 'Q5',  # replaced automatic 'Q30185' with 'Q5'
	'SupremeCourtOfTheUnitedStatesCase': '',
	'Coach': 'Q5',  # (manual)
	'LebanonSettlement': '',
	'SportsTeamMember': 'Q5',  # (manual)
	'NuclearPowerStation': '',
	'Bishop': 'Q5',  # (manual)
	'District': '',
	'TimePeriod': '',
	'Election': 'Q40231',
	'VideoGame': 'Q7889',
	'Mountain,Volcano': '',  # common attributes: ['firstAscent']
	'Painting': '',
	'Intercommunality': 'Q3153117',
	'MilitaryConflict_,_Attack': '',  # common attributes: ['weapon']
	'Artery': '',
	'Gene': 'Q7187',
	'GraveMonument': '',
	'Organization': 'Q43229',  # Q43229 = "organization"  # (manual)  # Instances tested: NATO (Q7184), FAO (Q82151); business (Q4830453) is also a subclass of Q43229!
	'CyclingTeam': '',
	'PoliticalFunction': '',
	'Musical': 'Q2743',
	'Priest': 'Q5',  # replaced automatic 'Q42603' with 'Q5'
	'Muscle': 'Q7365',
	'RoadJunction': '',
	'Cave': 'Q35509',
	'Politician': 'Q5',  # replaced automatic 'Q82955' with 'Q5'
	'NationalCollegiateAthleticAssociationAthlete': 'Q5',  # (manual)
	'SingleList': '',
	'GivenName': '',
	'ClericalAdministrativeRegion': '',
	'CityDistrict': '',
	'SpaceStation': '',
	'Engine': 'Q44167',  # Q44167 = "engine"  # (manual)  # Could not find any instances but Q44167 does have a subclass-of property!
	'HistoricBuilding': '',
	'RailwayTunnel': '',
	'GolfCourse': '',
	'On-SiteTransportation': '',
	'Escalator': '',
	'ConveyorSystem': '',
	'MovingWalkway': '',
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
