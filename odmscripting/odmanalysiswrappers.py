from __future__ import division
import os
from odmanalysis.scripts.FitRawODMData import fitRawODMData
from odmanalysis.scripts.MakeODMPlots import makeDisplacementPlots, makeIntensityProfilePlots
import json
from multiprocessing import Pool
import argparse
import odmanalysis as odm
import odmanalysis.gui as _gui
import os as _os


parser = argparse.ArgumentParser(prog="odm_analyze_all",
                                 description="Analyzes every measurement directory inside the current folder.")
 
parser.add_argument("--template",dest="templateMeasurement",type=str,default=None,
                    help="The directory that contains the fit settings that will be used for all the measurements.")

parser.add_argument("--use-template-profile",dest="useTemplateProfile",type=bool,default=False,
                    help="Use the first intensity profile from the template measurement to initialize the fit function")



def isMeasurement(d):
    isMeasurement = True
    isMeasurement &= os.path.isdir(d)
    isMeasurement &= os.path.exists(d + '/data.csv')
    isMeasurement &= not os.path.exists(d + '/odmanalysis.csv')

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


def analyzeAllMeasurementsAtPath(path,templateMeasurementPath,useTemplateProfile=False):
    odmSettingsFile = templatePath + '/odmSettings.ini'
    fitSettingsFile = templatePath + '/fitSettings.pcl'
    referenceIPDataFile = templatePath + '/data.csv' if args.useTemplateProfile else None
    
    
    dirlist = [os.path.join(path,d) for d in os.listdir(path) if isMeasurement(d)]
    
    
    
    #pool = Pool(1)
    #pool.map(doTask,[(d,odmSettingsFile,fitSettingsFile) for d in dirlist])
    #pool.close()
    
    for d in dirlist:
        analyzeMeasurement(d,odmSettingsFile,fitSettingsFile,referenceIPDataFile)


if __name__=="__main__":
    
    args = parser.parse_args()
    
    #templateMeasurement = r"D:\jkokorian\My Documents\_Delft\PhD\journal\2015-03-04 PM13.Tri4-C measurements\2015-03-04 16.12.03 Scripted Optical Displacement Measurement"
    if (args.templateMeasurement is not None and _os.path.exists(os.path.abspath(args.templateMeasurement)) and _os.path.isdir(os.path.abspath(args.templateMeasurement))):
        templateMeasurement = args.templateMeasurement

    else:
        templateMeasurement = _gui.get_dir_path()
    
    
    #templateMeasurement = args.templateMeasurement
    templatePath = os.path.abspath(templateMeasurement)
    analyzeAllMeasurementsAtPath()