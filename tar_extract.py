import argparse
import tarfile  # https://docs.python.org/3/library/tarfile.html
import os

def main():
	parser = argparse.ArgumentParser(
		description="""
		Extract (and possibly re-pack) a TAR archive,
		possibly limited to the first N files.
		""")

	parser.add_argument(
    	'tarPath',
    	type=str,
    	help="""The path to the TAR archive/file to extract.""",
    	metavar='TAR_FILE_PATH')

	parser.add_argument('-N',
		type=int,
		default=-1,
		help="""
		Only extract N files.
		By default, this is set to -1, which means it's deactivated.""",
		metavar='N')

	parser.add_argument('--re-pack',
		type=str,
		default='',
		help="""
		Re-pack the extracted files from the input TAR into this new TAR file.
		""",
		metavar='RE_PACK_DESTINATION_PATH')

	args = parser.parse_args()

	print("Unpacking...")

	tar = tarfile.open(args.tarPath)

	# When the file to extract is called "foo.tar",
	# extract into a folder called "foo":
	path_folder_to_extract_into: str = os.path.splitext(args.tarPath)[0]

	index: int = 0
	for tarinfo in tar:
		if index == args.N:
			break
		if tarinfo.isfile():  # (do not count directories)
			index += 1
		tar.extract(member=tarinfo, path=path_folder_to_extract_into)
		print(f"Extracted: {tarinfo.name}")
	tar.close()
	print(f"Finished unpacking of {index} files.")

	if args.re_pack != "":
		print("Re-packing...")
		new_tar = tarfile.open(args.re_pack, "w")
		for folder_item in sorted(os.listdir(path_folder_to_extract_into)):
			new_tar.add(os.path.join(path_folder_to_extract_into, folder_item))
		new_tar.close()
		print("Finished re-packing.")

if __name__ == "__main__":
	main()
