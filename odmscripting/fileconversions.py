import pandas as pd
import os
import json
import datetime

def dirIsMeasurementDirWithSettings(path):
    path = os.path.abspath(path)
    isValid = os.path.isdir(path)
    isValid &= os.path.exists(os.path.join(path, 'settings.json'))
    return isValid
    
def dirIsConvertibleMeasurement(path):
    path = os.path.abspath(path)
    return path.endswith("Displacement Measurement") and (os.path.exists(os.path.join(path, 'odmanalysis.csv')) or os.path.exists(os.path.join(path, 'data.csv')))

def getYearMonthDayFromMeasurementDir(path):
    path = os.path.abspath(path)
    year, month, day = os.path.split(path)[-1][:10].split('-')
    return year, month, day
    
def getYearMonthDayFromFilename(filename):
    filename = os.path.abspath(filename)
    fn = os.path.split(filename)[-1]
    year,month,day = fn[:10].split('-')    
    return year,month,day


def getProperColumnName(columnName):
    if columnName == "Actuation Settings JSON": 
        return "actuationSettings"
    elif columnName == "Image Aquisition Settings": 
        return "imageAcquisitionSettings"
    elif columnName == "Secondary DAQ Output Voltage Settings JSON": 
        return "secondaryDAQOutputVoltageSettings"
    else:
        return columnName




def tabulateSettingsAtPath(path):
    """
    Gets the settings.json files from all subdirectories in the path that and
    tabulates them into a single xlsx and hdf5 file.
    """
    experimentDirs = [f for f in os.listdir(path) if dirIsMeasurementDirWithSettings(os.path.join(path,f))]

    settings = {}
    for d in experimentDirs:
        with file(os.path.join(path,d,'settings.json'),'r') as f:
            settingsDict = json.loads(f.readlines()[0])
        measurementName = os.path.basename(d)

        df = pd.DataFrame(settingsDict).unstack().dropna()
        df['timestamp'] = datetime.datetime.strptime(measurementName[:19],'%Y-%m-%d %H.%M.%S')
        #df['timestamp'] = pd.to_datetime(measurementName[:20])
        settings[measurementName] = df

    dfMetadata = pd.DataFrame(settings).T

    dfMetadata.index.rename("measurementName",inplace=True)

    experimentName = os.path.split(os.path.abspath(path))[-1]
	

    xlsxFilename = experimentName + ' - settings.xlsx'
    print xlsxFilename
    dfMetadata.to_excel(os.path.join(path, xlsxFilename))

    properColumnNames = ['_'.join(col).strip('_') for col in [tuple([str(getProperColumnName(c)) for c in cTuple]) for cTuple in dfMetadata.columns]]
    dfMetadata.columns = pd.Index(properColumnNames)

    hdf5Filename = '%s - data.hdf5' % experimentName
    print hdf5Filename
    dfMetadata.to_hdf(os.path.join(path,hdf5Filename), 'settings')



def correctDatesInCsvFile(filePath, year, month, day, sep='\t', backup=True):

    with file(filePath,'r') as infile, file(filePath + '.new', 'w') as outfile:
        header = None
        for line in infile:
            if header is None:
                header = line
                outfile.write(header)
            else:
                date, time = line.split(sep)[0].split(' ')
                first, second, third = date.split('-')
                if (int(first) != int(year)):
                    #date format is dd-mm-yyyy or d-m-yyyy
                    newline = '-'.join([third,second,first]) + ' ' + time + line[line.index(sep):]
                    
                elif (int(second) != int(month)):
                    #data format is yyyy-dd-mm or yyyy-d-m                    
                    newline = '-'.join([first,third,second]) + ' ' + time + line[line.index(sep):]
                else:
                    newline = line
    
                outfile.write(newline)
    
    os.rename(filePath,filePath + ".old")
    os.rename(filePath + '.new',filePath)
    
    if backup == False:
        os.remove(filePath + ".old")




def convertNoImageDataFileToHDF5(path, deleteOriginal = False):
    """
    Converts a data.csv file that does not contain intensity profiles to HDF5.
    """
    print "reading data.csv..."
    df = pd.read_csv(path + '/data.csv',delimiter='\t',parse_dates='Timestamp',index_col='Timestamp')
    df.drop("Intensity Profile", axis=1,inplace=True)

    print "saving to data.hdf5"
    df.to_hdf(path + '/data.hdf5','measurement', complib='zlib', complevel=9)
    
    if (deleteOriginal):
        print "delete data.csv"
        os.remove(path + '/data.csv')


def convertOdmAnalysisFileToHDF5(path, deleteOriginal = False):
    print "reading odmanalysis.csv..."
    df = odm.readAnalysisData(path + '/odmanalysis.csv')
    
    print "saving to data.hdf5"
    df.to_hdf(path + '/odmanalysis.hdf5','odmanalysis', mode="a", complib='zlib', complevel=9)
    
    if (deleteOriginal):
        print "delete odmanalysis.csv"
        os.remove(path + '/odmanalysis.csv')


def getMeasurementDirsAtPath(path, recursive = False):
    if recursive == True:    
        return [os.path.join(basePath,directory) for basePath,directories,files in os.walk(path) for directory in directories if dirIsConvertibleMeasurement(os.path.join(path,basePath,directory))]
    else:
        return [d for d in os.listdir('.') if dirIsConvertibleMeasurement(d)]


def correctCsvFilesAtPath(path, recursive = False, backup=True):
    measurementPaths = getMeasurementDirsAtPath(path,recursive=recursive)
    
    for path in measurementPaths:
        year, month, day = os.path.split(path)[-1][:10].split('-')
        print "processing: " + path
        
        if os.path.exists(os.path.join(path,'data.csv')) and not os.path.exists(os.path.join(path, 'data.csv.old')):
            correctDatesInCsvFile(path, 'data.csv', year, month, day, backup=backup)
            
        if os.path.exists(os.path.join(path,'odmanalysis.csv')) and not os.path.exists(os.path.join(path,'odmanalysis.csv.old')):
            correctDatesInCsvFile(path, 'odmanalysis.csv', year, month, day, backup=backup)
            

def convertMeasurementFilesAtPathToHDF5(path, recursive = False, backup = True):
    measurementPaths = getMeasurementDirsAtPath(path,recursive=recursive)
        
    for path in measurementPaths:
        year, month, day = os.path.split(path)[-1][:10].split('-')
        print "processing: " + path
        if os.path.exists(os.path.join(path,'data.csv')) and not os.path.exists(os.path.join(path, 'data.csv.old')):
                        
            with file(path + '/settings.json') as settingsFile:
                settingsDict = json.load(settingsFile)
                
            if settingsDict["Image Aquisition Settings"]["picturesPerVoltage"] == 0:
                convertNoImageDataFileToHDF5(path,deleteOriginal=True)
                    
                    
        if os.path.exists(os.path.join(path,'odmanalysis.csv')) and not os.path.exists(os.path.join(path,'odmanalysis.csv.old')):
            correctDatesInCsvFile(path, 'odmanalysis.csv', year, month, day, backup=backup)
            