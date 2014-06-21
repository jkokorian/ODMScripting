
# coding: utf-8

# In[33]:

import json
import uuid


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
        return json.dumps(dict(method=self.method,params=self.params,id=self.id))
    
    def __repr__(self):
        return self.method



class SetImageAcquisitionSettingsRPC(ODMActionRPC):
    def __init__(self,imageAcquisitionSettings=None):
        ODMActionRPC.__init__(self,
                              method="SetImageAcquisitionParameters",
                              params=dict(imageAcquisitionSettings.__dict__))



class SetActuationSettingsRPC(ODMActionRPC):
    def __init__(self,actuatorSettings = None):
        ODMActionRPC.__init__(self,
                              method="SetActuationSettings",
                              params=dict(actuatorSettings.__dict__))



class SetSecondaryDAQOutputVoltageRPC(ODMActionRPC):
    def __init__(self,voltage=None):
        ODMActionRPC.__init__(self,
                              method="SetSecondaryDAQOutputVoltage",
                              params=dict(voltage=voltage))



class StartMeasurementRPC(ODMActionRPC):
    def __init__(self):
        ODMActionRPC.__init__(self,"RunMeasurement")



class PauseExecutionRPC(ODMActionRPC):
    def __init__(self,message=""):
        ODMActionRPC.__init__(self,"PauseExecution",
                              params=dict(message=message))



class ScriptFactory(object):
    def __init__(self):
        self.rpcBatch = []
    
    def StartMeasurement(self):
        self.rpcBatch.append(StartMeasurementRPC())
    
    def PauseExecution(self,message=""):
        self.rpcBatch.append(PauseExecutionRPC(message))
        
    def SetActuationSettings(self,actuationSettings):
        self.rpcBatch.append(SetActuationSettingsRPC(actuationSettings))
    
    def SetImageAcquisitionSettings(self,imageAcquisitionSettings):
        self.rpcBatch.append(SetImageAcquisitionSettingsRPC(imageAcquisitionSettings))
        
    def SetSecondaryDAQOutputVoltage(self,voltage):
        self.rpcBatch.append(SetSecondaryDAQOutputVoltageRPC(voltage))
    
    def to_script_file(self, path):
        with file(path,'w') as f:
           f.writelines([rpc.asjson() + '\n' for rpc in self.rpcBatch])
            
    def as_jsonRPCBatch(self):
        return "[" + ",".join([rpc.asjson() for rpc in self.rpcBatch]) + "]"
            






