from odmscripting import fileconversions
import os

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

@cli.command('test')
@click.argument('csvfile', type=click.Path(exists=True))
@click.option('--get-date-from', 'get_date_from', type=click.Choice(['dir','file']), default='file')
@click.option('--backup/--no-backup', default=True, help='backup the original file')
def test(csvfile,get_date_from,backup):
    path = os.path.abspath(csvfile)
    if (get_date_from == 'dir'):
        basepath = os.path.split(path)[0]
        year, month, day = fileconversions.getYearMonthDayFromMeasurementDir(basepath)
    elif (get_date_from == 'file'):
        year, month, day = fileconversions.getYearMonthDayFromFilename(path)
    fileconversions.test(path,year,month,day,backup=backup)

@cli.command('is-measurement', help='checks whether path is a valid odm measurement')
@click.argument('path', type=click.Path(exists=True))
def is_measurement(path):
    click.echo(fileconversions.dirIsMeasurementDirWithSettings(path))

@cli.command('correct-all-dates', help="Scans path for odm measurements folder and corrects the dates in all csv files inside")
@click.argument('path', type=click.Path(exists=True))
@click.option('--recurse/--no-recurse', default=False, help='search recursively')
@click.option('--backup/--no-backup', default=True, help='backup the original csv files')
def correct_all(path, recurse, backup):
    fileconversions.correctCsvFilesAtPath(path, recursive=recurse, backup=backup)





if __name__ == '__main__':
    cli()

