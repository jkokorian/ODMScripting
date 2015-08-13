import argparse
import os
from odmscripting.fileconversions import convertMeasurementFilesAtPathToHDF5

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="tabulate_settings",
                        description="Produces an excel file of all the settings.json files that are found inside the subfolders of the target path")
	parser.add_argument('path', metavar="path", type=str, default=".", help='The path in which to search for ODM measurement folders')
     

	args = parser.parse_args()

	if os.path.exists(args.path):
		convertMeasurementFilesAtPathToHDF5(args.path)
	else:
		print "invalid path"