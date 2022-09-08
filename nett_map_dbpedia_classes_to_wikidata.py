from typing import Dict

from attr_names_to_ontology_class import get_dbpedia_properties
from WikidataItem import WikidataItem


# 97 out of 283 DBpedia classes could be mapped to Wikidata entries
#   automatically using the code found in main() below:
dbpediaClassesMappedToWikidata: Dict[str, str] =\
{  # ToDo: map to human (Q5) !!!!! !!!!! !!!!! !!!!! !!!!!
	'Legislature': 'Q11204',
	'GrandPrix': '',
	'Athlete': '',
	'Person': 'Q215627',
	'Settlement': 'Q486972',
	'PopulatedPlace': '',
	'SpaceMission': '',
	'Organisation': 'Q43229',
	'Species': '',
	'Place': 'Q17334923',
	'Station': 'Q12819564',
	'FormulaOneRacer': '',
	'Planet': 'Q634',
	'PokerPlayer': '',
	'WrittenWork': '',
	'Department': '',
	'Canal': '',
	'Reference': '',
	'SkiResort': '',
	'Comedian': '',
	'Disease': 'Q12136',
	'LaunchPad': '',
	'River': 'Q4022',
	'Film': 'Q11424',
	'Spacecraft': 'Q40218',
	'Island': 'Q23442',
	'GolfPlayer': 'Q11303721',
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
	'MilitaryPerson': '',
	'TelevisionEpisode': '',
	'Event': 'Q1656682',
	'Olympics': '',
	'Woman': '',
	'MilitaryUnit': '',
	'Regency': '',
	'Boxer': '',
	'PoliticalParty': '',
	'Play': 'Q25379',
	'Airline': 'Q46970',
	'ChartsPlacements': '',
	'MusicGenre': '',
	'ReligiousBuilding': '',
	'AnatomicalStructure': '',
	'TennisPlayer': '',
	'Airport': 'Q1248784',
	'Mountain': 'Q8502',
	'ArchitecturalStructure': '',
	'GridironFootballPlayer': '',
	'Road': 'Q34442',
	'Work': 'Q386724',
	'MeanOfTransportation': '',
	'Company': '',
	'Memorial': '',
	'Museum': 'Q33506',
	'Sales': 'Q194189',
	'Country': 'Q6256',
	'MilitaryConflict': '',
	'Artist': 'Q483501',
	'Aircraft': 'Q11436',
	'Album': 'Q482994',
	'Saint': 'Q43115',
	'AutomobileEngine': '',
	'PowerStation': '',
	'Actor': 'Q33999',
	'MusicalWork': '',
	'SoccerPlayer': '',
	'RouteOfTransportation': '',
	'RomaniaSettlement': '',
	'Grape': 'Q10978',
	'Mill': 'Q44494',
	'AdministrativeRegion': '',
	'CollegeCoach': '',
	'Project': '',
	'ProtectedArea': '',
	'Family': 'Q8436',
	'Openswarm': '',
	'Criminal': 'Q2159907',
	'RadioStation': '',
	'CelestialBody': '',
	'IceHockeyPlayer': '',
	'Agent': 'Q24229398',
	'Statistic': 'Q1949963',
	'FormerMunicipality': '',
	'Municipality': '',
	'Organisation,_PopulatedPlace': '',
	'TelevisionShow': '',
	'Hotel': 'Q27686',
	'FictionalCharacter': '',
	'Automobile': '',
	'NorwaySettlement': '',
	'Scientist': 'Q901',
	'FigureSkater': '',
	'Animal': 'Q729',
	'Infrastructure': '',
	'Cemetery': 'Q39614',
	'HistoricPlace': '',
	'SnookerPlayer': '',
	'Race': '',
	'Instrument': '',
	'Language': 'Q34770',  # 2 candidates: 'Q315' and 'Q34770'
	'Galaxy': 'Q318',
	'Constellation': 'Q8928',
	'SoccerLeagueSeason': '',
	'BaseballPlayer': '',
	'Ship': '',
	'Opera': 'Q1344',
	'Letter': 'Q9788',  # 2 candidates: 'Q133492' (msg) and 'Q9788' (grapheme)
	'Brain': '',
	'ChemicalElement': '',
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
	'Man': '',
	'Building': 'Q41176',
	'MemberResistanceMovement': '',
	'SportsTeam': '',
	'ResearchProject': 'Q1298668',
	'Architect': '',
	'Currency': '',
	'SportCompetitionResult': '',
	'Blazon': '',
	'Software': 'Q7397',
	'PeriodicalLiterature': '',
	'LawFirm': '',
	'Rocket': 'Q41291',
	'ChemicalSubstance': '',
	'SoccerClub': '',
	'Attack': '',
	'Activity': 'Q1914636',
	'Biomolecule': 'Q206229',
	'Horse': '',
	'Outbreak': '',
	'Single': 'Q134556',
	'Song': '',
	'Writer': 'Q36180',
	'company': '',
	'Artwork': '',
	'SkiArea': '',
	'ChessPlayer': '',
	'College': '',
	'Globularswarm': '',
	'Cricketer': '',
	'OlympicResult': '',
	'GermanSettlement': '',
	'Document': '',
	'RestArea': '',
	'Band': 'Q215380',
	'Athlete,_CareerStation': '',
	'SoccerTournament': '',
	'ShoppingMall': 'Q31374404',
	'Magazine': 'Q41298',
	'SportsLeague': '',
	'Library': 'Q7075',
	'HungarySettlement': '',
	'GeneLocation': '',
	'Cleric': '',
	'TermOfOffice': '',
	'Train': 'Q870',
	'Colour': '',
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
	'MythologicalFigure': '',
	'Flag': 'Q14660',
	'RouteStop': '',
	'Restaurant': 'Q11707',
	'BodyOfWater': '',
	'SubMunicipality': '',
	'Drug': 'Q8386',
	'RaceTrack': '',
	'Locomotive': 'Q93301',
	'CareerStation': '',
	'Theatre': 'Q24354',
	'Monastry': '',
	'Plant': 'Q756',
	'MilitaryConflict_,_NaturalEvent_,_Attack': '',
	'VolleyballPlayer': '',
	'AdultActor': '',
	'Organisation,_Parish': '',
	'WorldHeritageSite': '',
	'City': 'Q515',
	'Wrestler': 'Q13474373',
	'core#Concept': '',
	'MountainRange': '',
	'OfficeHolder': '',
	'Diocese,_Parish': '',
	'Monarch': 'Q116',
	'MilitaryConflict,_AdministrativeRegion': '',
	'ChemicalCompound': '',
	'MusicalArtist': '',
	'TelevisionStation': '',
	'Law': '',
	'Astronaut': 'Q11631',
	'Continent': '',
	'Lake': 'Q23397',
	'Volcano': 'Q8072',
	'SwitzerlandSettlement': '',
	'Swimmer': 'Q10843402',
	'WaterwayTunnel': '',
	'Mayor': 'Q30185',
	'SupremeCourtOfTheUnitedStatesCase': '',
	'Coach': '',
	'LebanonSettlement': '',
	'SportsTeamMember': '',
	'NuclearPowerStation': '',
	'Bishop': '',
	'District': '',
	'TimePeriod': '',
	'Election': 'Q40231',
	'VideoGame': 'Q7889',
	'Mountain,Volcano': '',
	'Painting': '',
	'Intercommunality': 'Q3153117',
	'MilitaryConflict_,_Attack': '',
	'Artery': '',
	'Gene': 'Q7187',
	'GraveMonument': '',
	'Organization': '',
	'CyclingTeam': '',
	'PoliticalFunction': '',
	'Musical': 'Q2743',
	'Priest': 'Q42603',
	'Muscle': 'Q7365',
	'RoadJunction': '',
	'Cave': 'Q35509',
	'Politician': 'Q82955',
	'NationalCollegiateAthleticAssociationAthlete': '',
	'SingleList': '',
	'GivenName': '',
	'ClericalAdministrativeRegion': '',
	'CityDistrict': '',
	'SpaceStation': '',
	'Engine': '',
	'HistoricBuilding': '',
	'RailwayTunnel': '',
	'GolfCourse': '',
	'On-SiteTransportation': '',
	'Escalator': '',
	'ConveyorSystem': '',
	'MovingWalkway': '',
	'GeopoliticalOrganisation': '',
	'LunarCrater': '',
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
					f"for DBpedia class name '{dbpedia_class_name}''): " +\
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
