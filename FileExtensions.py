class FileExtensions:  # ToDo: USE !!!!! !!!!!
	def __init__(\
		CSV_extensions: List[str] = None,\
		XLSX_extensions: List[str] = None,\
		JSON_extensions: List[str] = None,\
		TAR_extensions: List[str] = None):
		self.CSV_extensions = CSV_extensions\
			if CSV_extensions is not None and CSV_extensions != []\
			else [".csv"]
		self.XLSX_extensions = XLSX_extensions\
			if XLSX_extensions is not None and XLSX_extensions != []\
			else [".xlsx", ".xls"]
		self.JSON_extensions = JSON_extensions\
			if JSON_extensions is not None and JSON_extensions != []\
			else [".json"]
		self.TAR_extensions = TAR_extensions\
			if TAR_extensions is not None and TAR_extensions != []\
			else [".tar"]
