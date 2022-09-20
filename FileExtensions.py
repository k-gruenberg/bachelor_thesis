from typing import List

class FileExtensions:
	def __init__(self,\
		CSV_extensions: List[str] = None,\
		XLSX_extensions: List[str] = None,\
		JSON_extensions: List[str] = None,\
		TAR_extensions: List[str] = None):
		self.CSV_extensions = CSV_extensions\
			if CSV_extensions is not None and CSV_extensions != []\
			else [".csv"]
		self.XLSX_extensions = XLSX_extensions\
			if XLSX_extensions is not None and XLSX_extensions != []\
			else [".xlsx"]  # wrong: [".xlsx", ".xls"]
		"""
		openpyxl.utils.exceptions.InvalidFileException:
		openpyxl does not support the old .xls file format,
		please use xlrd to read this file,
		or convert it to the more recent .xlsx file format.
		"""
		self.JSON_extensions = JSON_extensions\
			if JSON_extensions is not None and JSON_extensions != []\
			else [".json"]
		self.TAR_extensions = TAR_extensions\
			if TAR_extensions is not None and TAR_extensions != []\
			else [".tar"]
