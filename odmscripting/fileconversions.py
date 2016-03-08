import pandas as pd
import os
import json
import datetime
import odmanalysis as odm

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




def readMeasurementSettingsAtPath(path):
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
    
    

    return dfMetadata


def flattenSettingsDataFrameColumns(dfMetadata):
    column_to_dtype_dict = {
    'timestamp': 'int64',
    'actuationSettings_actuationFrequency': 'float',
    'actuationSettings_amplification': 'float',
    'actuationSettings_amplitude': 'float',
    'actuationSettings_dcOffset': 'float',
    'actuationSettings_numberOfCycles': 'int64',
    'actuationSettings_numberOfSteps': 'int64',
    'actuationSettings_offsetRampSpeed': 'float',
    'actuationSettings_waveformType': 'string',
    'imageAcquisitionSettings_picturesPerVoltage': 'int64',
    'imageAcquisitionSettings_showVideoDuringMeasurement': 'bool',
    'imageAcquisitionSettings_summingMode': 'string',
    'imageAcquisitionSettings_waitBeforeCapture': 'float',
    'secondaryDAQOutputVoltageSettings_externalAmplification': 'float',
    'secondaryDAQOutputVoltageSettings_voltage': 'float'
    }

    properColumnNames = ['_'.join(col).strip('_') for col in [tuple([str(getProperColumnName(c)) for c in cTuple]) for cTuple in dfMetadata.columns]]
    dfMetadata.columns = pd.Index(properColumnNames)
    
    for c in dfMetadata.columns:
        s = dfMetadata[c]
        dfMetadata[c] = pd.Series(s,dtype=column_to_dtype_dict[c])
    
    
def tabulateSettingsAtPath(path):
    """
    Gets the settings.json files from all subdirectories in the path that and
    tabulates them into a single xlsx and hdf5 file.
    """
    dfMetadata = readMeasurementSettingsAtPath(path)

    experimentName = os.path.split(os.path.abspath(path))[-1]
    
    

    xlsxFilename = experimentName + ' - settings.xlsx'
    print xlsxFilename
    dfMetadata.to_excel(os.path.join(path, xlsxFilename))

    flattenSettingsDataFrameColumns(dfMetadata)

    hdf5Filename = '%s - data.hdf5' % experimentName
    print hdf5Filename
    dfMetadata.to_hdf(os.path.join(path,hdf5Filename), 'settings', format='table',data_columns=True)
    

def dirContainsMeasurements(path):
    return os.path.isdir(path) and any([d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d)) and dirIsMeasurementDirWithSettings(os.path.join(path,d))])


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




def convertNoImageDataFileToHDF5(path, keep_original = False):
    """
    Converts a data.csv file that does not contain intensity profiles to HDF5.
    """
    print "reading data.csv..."
    df = pd.read_csv(path + '/data.csv',delimiter='\t',parse_dates='Timestamp',index_col='Timestamp')
    df.drop("Intensity Profile", axis=1,inplace=True)

    print "saving to data.hdf5"
    df.to_hdf(path + '/data.hdf5','measurement', complib='zlib', complevel=9, format='table', data_columns=True)
    
    if not keep_original:
        print "delete data.csv"
        os.remove(path + '/data.csv')


def convertOdmAnalysisFileToHDF5(path, keep_original = True):
    print "reading odmanalysis.csv..."
    df = odm.readAnalysisData(path + '/odmanalysis.csv')
    
    print "saving to data.hdf5"
    df.to_hdf(path + '/odmanalysis.hdf5','odmanalysis', mode="a", complib='zlib', complevel=9, format='table', data_columns=True)
    
    if not keep_original:
        print "delete odmanalysis.csv"
        os.remove(path + '/odmanalysis.csv')


def getMeasurementDirsAtPath(basePath, recursive = False):
    if recursive == True:    
        return [os.path.join(path,directory) for path,directories,files in os.walk(basePath) for directory in directories if dirIsConvertibleMeasurement(os.path.join(basePath,path,directory))]
    else:
        return [d for d in os.listdir(basePath) if dirIsConvertibleMeasurement(d)]


def getGasSystemLogFilesAtPath(basePath):
    return [f for f in os.listdir(basePath) if f.endswith("Gas System Log.csv")]





def correctRawDataCsvFilesAtPath(path,recursive=False,keep_originals=True):
    measurementPaths = getMeasurementDirsAtPath(path,recursive=recursive)
    
    for measurementPath in measurementPaths:
        year, month, day = getYearMonthDayFromMeasurementDir(measurementPath)
        print "processing: " + measurementPath
        
        dataCsvPath = os.path.join(measurementPath,'data.csv')
        if os.path.exists(dataCsvPath) and not os.path.exists(dataCsvPath + ".old"):
            correctDatesInCsvFile(dataCsvPath, year, month, day, backup=keep_originals)
            
def correctOdmAnalysisCsvFilesAtPath(path,recursive=False,keep_originals=True):
    for measurementPath in getMeasurementDirsAtPath(path,recursive=recursive):
        year, month, day = getYearMonthDayFromMeasurementDir(measurementPath)
                    
        odmanalysisCsvPath = os.path.join(measurementPath,'odmanalysis.csv')
        print "processing %s" % odmanalysisCsvPath
        if os.path.exists(odmanalysisCsvPath) and not os.path.exists(odmanalysisCsvPath + '.old'):
            correctDatesInCsvFile(odmanalysisCsvPath, year, month, day, backup=keep_originals,sep=",")

def correctGasSystemCsvFilesAtPath(path,keep_originals=True):
    gasSystemLogFilePaths = [os.path.join(path,f) for f in getGasSystemLogFilesAtPath(path)]
    for gasSystemLogFilePath in gasSystemLogFilePaths:
        if os.path.exists(gasSystemLogFilePath) and not os.path.exists(gasSystemLogFilePath + '.old'):
            year, month, day = getYearMonthDayFromFilename(gasSystemLogFilePath)
            correctDatesInCsvFile(gasSystemLogFilePath, year, month, day, backup=keep_originals)


def correctAllCsvFilesAtPath(path, recursive = False, backup=True):
    measurementPaths = getMeasurementDirsAtPath(path,recursive=recursive)
    
    for measurementPath in measurementPaths:
        year, month, day = getYearMonthDayFromMeasurementDir(measurementPath)
        print "processing: " + measurementPath
        
        dataCsvPath = os.path.join(measurementPath,'data.csv')
        if os.path.exists(dataCsvPath) and not os.path.exists(dataCsvPath + ".old"):
            correctDatesInCsvFile(dataCsvPath, year, month, day, backup=backup)
            
        odmanalysisCsvPath = os.path.join(measurementPath,'odmanalysis.csv')
        if os.path.exists(odmanalysisCsvPath) and not os.path.exists(odmanalysisCsvPath + '.old'):
            correctDatesInCsvFile(odmanalysisCsvPath, year, month, day, backup=backup,sep=",")
    
    gasSystemLogFilePaths = getGasSystemLogFilesAtPath(path)
    for gasSystemLogFilePath in gasSystemLogFilePaths:
        if os.path.exists(gasSystemLogFilePath) and not os.path.exists(gasSystemLogFilePath + '.old'):
            year, month, day = getYearMonthDayFromFilename(gasSystemLogFilePath)
            correctDatesInCsvFile(gasSystemLogFilePath, year, month, day, backup=backup)



def convertMeasurementFilesAtPathToHDF5(path, recursive = False, keep_data_csv = False, keep_odmanalysis_csv = True):
    measurementPaths = getMeasurementDirsAtPath(path,recursive=recursive)
        
    for path in measurementPaths:
        year, month, day = os.path.split(path)[-1][:10].split('-')
        print "processing: " + path
        if os.path.exists(os.path.join(path,'data.csv')):
                        
            with file(path + '/settings.json') as settingsFile:
                settingsDict = json.load(settingsFile)
                
            if settingsDict["Image Aquisition Settings"]["picturesPerVoltage"] == 0:
                convertNoImageDataFileToHDF5(path, keep_original = keep_data_csv)
                    
                    
        if os.path.exists(os.path.join(path,'odmanalysis.csv')):
            convertOdmAnalysisFileToHDF5(os.path.join(path,'odmanalysis.csv'), year, month, day, keep_original=keep_odmanalysis_csv)
            