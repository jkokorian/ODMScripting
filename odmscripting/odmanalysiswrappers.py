from __future__ import division
import os
from odmanalysis.scripts.FitRawODMData import fitRawODMData
from odmanalysis.scripts.MakeODMPlots import makeDisplacementPlots, makeIntensityProfilePlots
import json
from multiprocessing import Pool
import argparse
import odmanalysis as odm
import odmanalysis.gui as _gui
import fileconversions




def isMeasurement(d):
    isMeasurement = True
    isMeasurement &= os.path.isdir(d)
    isMeasurement &= os.path.exists(d + '/data.csv')
    isMeasurement &= os.path.exists(d + '/settings.json')

    if not isMeasurement:
        return isMeasurement
    
    with file(d + './settings.json','r') as f:
        settingsDict = json.load(f)
    
    isMeasurement &= settingsDict['Image Aquisition Settings']["picturesPerVoltage"] != 0
    isMeasurement &= settingsDict['Actuation Settings JSON']["numberOfCycles"] > 1
    return isMeasurement

def analyzeMeasurement(path, odmSettingsFile, fitSettingsFile, referenceIPDataFile):
    print "analyzing " + path    
    datafile = path + '/data.csv'
    
    commonPath = os.path.abspath(os.path.split(datafile)[0])
    measurementName = os.path.split(commonPath)[1]
    
    
    settings = odm.CurveFitSettings.loadFromFile(odmSettingsFile)
    df,movingPeakFitSettings,referencePeakFitSettings,measurementName = fitRawODMData(datafile,settingsFile=odmSettingsFile, fitSettingsFile=fitSettingsFile,referenceIPDataFile=referenceIPDataFile)
    settings.saveToFile(commonPath + '/odmSettings.ini')    
    
    plotKwargs = {'savePath' : commonPath, 'measurementName' : measurementName, 'nmPerPx' : settings.pxToNm}
    makeDisplacementPlots(df, **plotKwargs)
    makeIntensityProfilePlots(df, movingPeakFitSettings,referencePeakFitSettings, **plotKwargs)


def doTask(args):
    analyzeMeasurement(*args)


def analyzeAllMeasurementsAtPath(path,templateMeasurementPath,useTemplateProfile=False,useTemplateSettings=True,skipExisting=False):
    templateOdmSettingsFile = templateMeasurementPath + '/odmSettings.ini' if useTemplateSettings else None
    templateFitSettingsFile = templateMeasurementPath + '/fitSettings.pcl' if useTemplateSettings else None
    referenceIPDataFile = templateMeasurementPath + '/data.csv' if useTemplateProfile else None
    
    
    dirlist = [os.path.join(path,d) for d in os.listdir(path) if fileconversions.dirIsMeasurementDirWithSettings(d) and isMeasurement(d) and (not fileconversions.isAnalyzedMeasurementDir(path) or not skipExisting)]
    for d in dirlist:
        print d
    
    
    
    #pool = Pool(1)
    #pool.map(doTask,[(d,odmSettingsFile,fitSettingsFile) for d in dirlist])
    #pool.close()
    
    for d in dirlist:
        if os.path.abspath(d) != os.path.abspath(templateMeasurementPath):
            odmSettingsFile = templateOdmSettingsFile if useTemplateSettings else os.path.join(d,'odmSettings.ini')
            fitSettingsFile = templateFitSettingsFile if useTemplateSettings else os.path.join(d,'fitSettings.pcl')
            analyzeMeasurement(d,odmSettingsFile,fitSettingsFile,referenceIPDataFile)


