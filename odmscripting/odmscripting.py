
# coding: utf-8

# In[33]:

import json
import uuid
from scipy.optimize import fsolve
from numpy import logspace,log10,sum

def logspace_cumsum(start,total,steps):
    """
    Generate logaritmically spaced numbers such that their sum equals 'sum'.
    """
    stopValue = fsolve(lambda stop: sum(logspace(log10(start),stop,steps)) - total, log10(total))[0]
    return logspace(1,stopValue,steps)


class ROISettings(object):
    def __init__(self,x=None,y=None,width=None,height=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height        


class ExposureSettings(object):
    def __init__(self,exposureTime=None, gain=None, blacklevelOffset=None):
        self.exposureTime = exposureTime
        self.gain = gain
        self.blacklevelOffset = blacklevelOffset


class ActuationSettings(object):
        
    def __init__(self, actuationFrequency=None,amplitude=None,amplification=None,waveformType=None,dcOffset=None,offsetRampSpeed=None,numberOfSteps=None,numberOfCycles=None):
        self.actuationFrequency=actuationFrequency
        self.amplitude = amplitude
        self.amplification = amplification
        self.waveformType = waveformType
        self.dcOffset = dcOffset
        self.offsetRampSpeed = offsetRampSpeed
        self.numberOfSteps = numberOfSteps
        self.numberOfCycles = numberOfCycles


class ImageAcquisitionSettings(object):
    
    
    def __init__(self,picturesPerVoltage=None,waitBeforeCapture=None,showVideoDuringMeasurement=None,summingMode=None):
        self.picturesPerVoltage = picturesPerVoltage
        self.waitBeforeCapture = waitBeforeCapture
        self.showVideoDuringMeasurement = showVideoDuringMeasurement
        self.summingMode = summingMode
        
    

class DAQOutputChannelSettings(object):
    
    def __init__(self,voltage=None,externalAmplification=None):
        self.voltage = voltage
        self.externalAmplification = externalAmplification




class WaveformType:
    SquareRoot = "SquareRoot"
    Triangle = "Triangle"
    HalfTriangle = "Half-Triangle"
    Sine = "Sine"



class ODMActionRPC(object):
    
    def __init__(self,method,params = dict()):
        self.method = method
        self.params = params
        self.id = str(uuid.uuid4())
    
    def asjson(self):
        return json.dumps(dict(method=self.method,params=self.params,id=self.id,jsonrpc="2.0"))
    
    def __repr__(self):
        return self.method



class SetImageAcquisitionSettingsRPC(ODMActionRPC):
    def __init__(self,imageAcquisitionSettings=None):
        ODMActionRPC.__init__(self,
                              method="SetImageAcquisitionSettings",
                              params=dict(imageAcquisitionSettings.__dict__))



class SetActuationSettingsRPC(ODMActionRPC):
    def __init__(self,actuatorSettings = None):
        ODMActionRPC.__init__(self,
                              method="SetActuationSettings",
                              params=dict(actuatorSettings.__dict__))



class SetSecondaryDAQOutputSettingsRPC(ODMActionRPC):
    def __init__(self,daqOutputChannelSettings):
        ODMActionRPC.__init__(self,
                              method="SetSecondaryDAQOutputSettings",
                              params=dict(daqOutputChannelSettings.__dict__))


class SetROISettingsRPC(ODMActionRPC):
    def __init__(self,roiSettings=None):
        ODMActionRPC.__init__(self,
                              method="SetROISettings",
                              params=dict(roiSettings.__dict__))


class SetExposureSettingsRPC(ODMActionRPC):
    def __init__(self,exposureSettings=None):
        ODMActionRPC.__init__(self,
                              method="SetExposureSettings",
                              params=dict(exposureSettings.__dict__))


class StartMeasurementRPC(ODMActionRPC):
    def __init__(self):
        ODMActionRPC.__init__(self,"StartMeasurement")



class PauseExecutionRPC(ODMActionRPC):
    def __init__(self,message=""):
        ODMActionRPC.__init__(self,"PauseExecution",
                              params=dict(message=message))


class ZMQServiceRPC(ODMActionRPC):
    def __init__(self,endpoint,method,paramsDict):
        ODMActionRPC.__init__(self,"Ext/%s/%s" % (endpoint,method),
                              params=paramsDict)
        


class ScriptFactory(object):
    def __init__(self):
        self.rpcBatch = []
    
    def startMeasurement(self):
        self.rpcBatch.append(StartMeasurementRPC())
    
    def pauseExecution(self,message=""):
        self.rpcBatch.append(PauseExecutionRPC(message))
        
    def setActuationSettings(self,actuationSettings):
        self.rpcBatch.append(SetActuationSettingsRPC(actuationSettings))
    
    def setImageAcquisitionSettings(self,imageAcquisitionSettings):
        self.rpcBatch.append(SetImageAcquisitionSettingsRPC(imageAcquisitionSettings))
        
    def setSecondaryDAQOutputSettings(self,daqOutputChannelSettings):
        self.rpcBatch.append(SetSecondaryDAQOutputSettingsRPC(daqOutputChannelSettings))
    
    def setROISettings(self,roiSettings):
        self.rpcBatch.append(SetROISettingsRPC(roiSettings))
        
    def setExposureSettings(self,exposureSettings):
        self.rpcBatch.append(SetExposureSettingsRPC(exposureSettings))
    
    def callZMQService(self,zmqServiceRPC):
        self.rpcBatch.append(zmqServiceRPC)
        
    def addRPC(self,odmActionRPC):
        self.rpcBatch.append(odmActionRPC)
    
    def to_script_file(self, path):
        with file(path,'w') as f:
           f.writelines([rpc.asjson() + '\n' for rpc in self.rpcBatch])
            
    def as_jsonRPCBatch(self):
        return "[" + ",".join([rpc.asjson() for rpc in self.rpcBatch]) + "]"
            






