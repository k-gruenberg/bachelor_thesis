class FileExtensions:  # ToDo: USE !!!!! !!!!!
	def __init__(\
		csv_extensions: List[str] = [],\
		xlsx_extensions: List[str] = [],\
		json_extensions: List[str] = [],\
		tar_extensions: List[str] = []):
		self.csv_extensions = csv_extensions\
			if csv_extensions != [] else [".csv"]
		self.xlsx_extensions = xlsx_extensions\
			if xlsx_extensions != [] else [".xlsx", ".xls"]
		self.json_extensions = json_extensions\
			if json_extensions != [] else [".json"]
		self.tar_extensions = tar_extensions\
			if tar_extensions != [] else [".tar"]
