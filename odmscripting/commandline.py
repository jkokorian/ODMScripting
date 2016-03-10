import fileconversions
import os
import odmanalysiswrappers

import click

@click.group()
def cli():
    pass

@cli.command('list-measurements', help='List all measurement in path')
@click.argument('path', type=click.Path(exists=True))
@click.option('--recurse/--no-recurse', default=False, help='search recursively')
def list_measurements(path,recurse):
    for measurementDir in fileconversions.getMeasurementDirsAtPath(path, recursive=recurse):
        click.echo(measurementDir)

@cli.command('correct-csv-dates', help="""
corrects the date format in the target csv file. The first column should contain the date.

Currently supports:

    data.csv
    odmanalysis.csv
    YYYY-MM-DD Gas System Log.csv
""")
@click.argument('csvfile', type=click.Path(exists=True))
@click.option('--get-date-from', 'get_date_from', type=click.Choice(['dir','file']), default='file')
@click.option('--backup/--no-backup', default=True, help='backup the original file')
def correct_csv_dates(csvfile,get_date_from,backup):
    path = os.path.abspath(csvfile)
    if (get_date_from == 'dir'):
        basepath = os.path.split(path)[0]
        year, month, day = fileconversions.getYearMonthDayFromMeasurementDir(basepath)
    elif (get_date_from == 'file'):
        year, month, day = fileconversions.getYearMonthDayFromFilename(path)
        print year, month, day
    fileconversions.correctDatesInCsvFile(path,year,month,day,backup=backup)


@cli.command('is-measurement', help='checks whether path is a valid odm measurement')
@click.argument('path', type=click.Path(exists=True))
def is_measurement(path):
    click.echo(fileconversions.dirIsMeasurementDirWithSettings(path))


@cli.command('correct-all-csv-files', help="Scans path for odm measurements folder and corrects the dates in all csv files inside")
@click.argument('path', type=click.Path(exists=True))
@click.option('--recurse/--no-recurse', default=False, help='search recursively')
@click.option('--backup/--no-backup', default=True, help='backup the original csv files')
def correct_all(path, recurse, backup):
    fileconversions.correctAllCsvFilesAtPath(path, recursive=recurse, backup=backup)

@cli.command('csv-to-hdf', help="Scans path for odm measurements folders and converts all csv files to hdf5")
@click.argument('path', type=click.Path(exists=True))
@click.argument('--keep-datacsv/--delete-datacsv','keep_data_data', default=False)
@click.argument('--keep-odmanalysiscsv/--delete-odmanalysiscsv','keep_odmanalysis_csv',default=True)
def csv_to_hdf(path,recurse, keep_data_csv,keep_odmanalysis_csv):
    fileconversions.convertMeasurementFilesAtPathToHDF5(path, recursive=recurse, keep_data_csv=keep_data_csv,keep_odmanalysis_csv=keep_odmanalysis_csv)


@cli.command('combine-settings-files', help="Combines all gas system log files in the path into a single hdf5 file.")
@click.argument('path', type=click.Path(exists=True))
def tabulate_settings_files(path):
    fileconversions.tabulateSettingsAtPath(path)
    

@cli.command('analyze-all-measurements', help="Analyzes all measurements at the target path with the settings from a template measurement")
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--template', 'template_path', type=click.Path(exists=True), help="Path to the measurement to use as a template")
@click.option('--use-template-profile/--no-use-template-profile','use_template_profile',default=False, help="Use the first profile of the template measurement to initialize the fit functions")
@click.option('--use-template-settings/--no-use-template-settings','use_template_settings',default=True, help="Use the settings from the template measurement")
def analyze_all_measurements(path,template_path,use_template_profile,use_template_settings):
    template_path = os.path.abspath(template_path)
    odmanalysiswrappers.analyzeAllMeasurementsAtPath(path,template_path,use_template_profile,use_template_settings)



if __name__ == '__main__':
    cli()

