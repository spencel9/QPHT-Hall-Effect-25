# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 13:39:34 2025

@author: QPHTLab
"""

#Inheritances
import numpy as np
import matplotlib.pyplot as pm
import csv as CSV
from datetime import datetime
from time import  strftime
from pymeasure.instruments.keithley import Keithley2450,Keithley2400
from pymeasure.experiment.parameters import FloatParameter, IntegerParameter
from pymeasure.experiment.procedure import Procedure
from pymeasure.experiment.results import Results
from pymeasure.experiment.workers import Worker 
from pymeasure.display import Plotter
from pymeasure.log import log, console_log
#Procedure
class PlotIV(Procedure):   
    # Initializaiton
    SMU = Keithley2450('GPIB::18::INSTR', name= "SMU") #locates the sourcemeter at the specified address
    SMU.use_front_terminals() #instructs the sourcemeter to measure from the front terminals
    SMU.reset() #resets the sourcemeter current and voltage to zero.
    #SMU.source_mode = 'current'
    # Parameters
    V_Source = IntegerParameter("V_Source", units= None, minimum= -1, maximum= 2) #binary option which determines if the SMU sources voltage (1) or current (0).
    DATA_COLUMNS = [] #blank array so that the data columns can be labelled according to the choice of V_Source   
        # Initializaiton
    Data_Points = IntegerParameter(name="Data_Points", units=None, minimum=10, maximum= 10000, step=None,default= 10) #number of data-points
    Measurements = IntegerParameter(name="Measurements",units= None, minimum= 1, maximum= 10000, step= None, default= 100) # number of voltage measurments per data-point
    Int_Data = int(str(Data_Points)) #ensures that Data_Points is interpreted as an integer.
    Int_Measurements = int(str(Measurements)) #ensures that Measurements is interpreted as an integer by the compiler.
    I_min = FloatParameter("Minimum Current", units= None, minimum= -105, maximum= 1e-15, decimals= 15, default= -1e-3) #sets the minimum current (default = 10.0 A)
    I_min = FloatParameter("Minimum Current", units= None, minimum= -105, maximum= 1e-15, decimals= 15, default= -1e-3) #sets the minimum current (default = 10.0 A)
    #sets the step by which the current will increase between measurements.
    I_max = FloatParameter("Maximum Current", units= None, minimum= 0, maximum= 105, decimals= 15, default = 1e-3) #sets the maximum current (default = 100.0 A)
    I_min_float = float(str(I_min)) #ensures that I_min is interpreted as a floating-point number by the compiler.
    I_max_float = float(str(I_max)) #ensures that I_max is interpreted as a floating-point number by the compiler. 
    #I_Step = (I_max_float-I_min_float)/Int_Data #the step in current between each data-point.
    J = np.linspace(I_min_float,I_max_float,num= Int_Data) #sets the currents at which each measurement is to take place.
    I =[]  #empty array to be filled with currents
    R = np.zeros([Int_Data,Int_Measurements]) #empty array to be filled with voltage measurments
    Ravg = [] #empty array to be filled with average voltages
    SigmaR = [] #empty array to be filled with standard deviation of voltage
    Phi_Max = FloatParameter('V_Max', units= None, minimum = -21.00, maximum = 21.00, decimals = 15, default = 3.00) # The limits of the voltage-range over which measurements are made.
    PhiM = float(str(Phi_Max)) # Converts the voltage-limit to a float parameter.
    PhiR = PhiM+1.00 # The actual limit to be set for the allowed voltages.
    Phi = np.linspace(-PhiM, PhiM, Int_Data) # Sets the voltages at which measurements will be made.
    Epsilon = np.zeros([Int_Data,Int_Measurements]) # Array of zeroes to be replaced with current-measurements.
    Epsilon_avg = [] # Empty array to be filled with average current values.
    Sigma_Epsilon = [] # Empty array to be filled with standard deviations in the current.
    def Wake_Up_Call(self):
        if (self.V_Source == 0):
           self.DATA_COLUMNS = ['Current (A)','Resistance in Ohms', 'Standard Deviation'] # informs the Results Class how to arrange data in the output file.
           self.SMU.use_front_terminals() #instructs the sourcemeter to measure from the front terminals
           self.SMU.reset() #resets the sourcemeter current and voltage to zero.
           self.SMU.apply_current() #informs the sourcemeter to act as a current source.
           self.SMU.wires = 4 #Sets the Sourcemeter to 4-wire mode so that a 4-probe measurement can be made.
           self.SMU.compliance_voltage = 100
           self.SMU.source_current_range = self.I_max_float #sets the voltage range to 20 V.
           self.SMU.measure_resistance() #informs the sourcemeter to measure resistance.
           self.SMU.enable_source() #enables the SMU to act as a source of current through the sample.
        elif (self.V_Source == 1):
            self.DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Standard Deviation (V)'] # informs the Results Class how to arrange data in the output file.
            self.SMU.use_front_terminals() #Tells the SMU to measure using the front terminals.
            self.SMU.reset()
            self.SMU.apply_voltage() # Informs the sourcemeter to act as a voltage-source.
            self.SMU.source_voltage_range = self.PhiR #Sets the allwed range of voltages for the SMU.
            self.SMU.measure_current # Informs the SMU to measure the current.
            self.SMU.compliance_current = 1.05 # Sets the compliance current for the SMU.
            self.SMU.enable_source() # Permits the sourcemeter to source the voltage.
    def Measurement(self, Work):
        if (self.V_Source == 0):
            def Measurement(self,Work):
             for i in range(self.Int_Data):
                  Ii = self.J[i]
                  self.I = np.append(self.I,[Ii]) #sets the current for the particular data-point.
                  self.Wake_Up_Call() #enables the SMU to act as a source of current for the sample.
                  self.SMU.ramp_to_current(Ii,steps= 10, pause= 1e-3) #ramps the sourcemeter to the next current
                  for j in range(self.Int_Measurements):
                      self.R[i,j] = self.SMU.resistance #measures the voltage at the set current   
                  Ri = np.mean(self.R[i,:]) #arithmetic mean of the ith voltage-value.
                  self.Ravg = np.append(self.Ravg, [Ri]) # stores the ith voltage-value in Vavg.
                  SigmaRi = np.std(self.R[i,:]) #computes the standard deviaiton in the voltages measured at each current
                  self.SigmaR = np.append(self.SigmaR, [SigmaRi]) #stores the ith standard deviation in the SigmaV array.
                  Row_i = [i,Ri,Ii,SigmaRi]
                #Outputs
                  print(Row_i) #prints the results of the most recent measurement.
                  DATA = { 
                           'Current (A)': Ii,
                           'Resistance in Ohms': Ri,
                           'Standard Deviation': SigmaRi
                           } #data to be recorded in the CSV file.
                  Work.emit('results',DATA)
                  self.SMU.shutdown()
        elif (self.V_Source == 1):
                for i in range(self.Int_Data):
                     Phi_i = self.Phi[i]
                     self.Wake_Up_Call()
                     self.SMU.ramp_to_voltage(Phi_i, steps= 5, pause= 1e-5)
                     for j in range(self.Int_Measurements):
                          self.Epsilon[i,j] = self.SMU.current # Measures the current at the applied voltage.
                     Epsilon_i = np.mean(self.Epsilon[i,:]) # computes the average current at the applied voltage.
                     Sigma_i = np.std(self.Epsilon[i,:]) # computes the standard deviation in the current at the applied voltage.
                     self.Epsilon_avg = np.append(self.Epsilon_avg, [Epsilon_i]) # Saves the average current into the data-array.
                     self.Sigma_Epsilon = np.append(self.Sigma_Epsilon,[Sigma_i]) # Saves the standard deviation into the data-array."""
                     Data = {'Voltage (V)': Phi_i,
                              'Current (A)': Epsilon_i,
                              'Standard Deviation (A)': Sigma_i
                                 } # Data to be emitted to the CSV file.
                     Work.emit('results', Data) # Records the collected data in the output file.
                     self.SMU.shutdown() # Shuts down the sourcemeter.
            
#Workers
console_log(log)
#og.info('Making a measurement.')
Plot = PlotIV()
Plot.V_Source = 0
Plot.Data_Points = 10
Plot.Measurements = 10
Plot.I_min = -10
Plot.I_max = 10
log.info('Creating a record.')
now = datetime.now()
Now = now.strftime('%b-%d-%Y-%I-%M-%S') #creates a string recording the current date and time.
file_name = 'PlotIV-Multi_Source-Results-'+ Now +'.csv' #generates a unique file-name for each run.
results = Results(Plot, file_name) #results to be pulled from the above procedurelog.info('Creating a real-time plot in the UI.')
PRT = Plotter(results, refresh_time= 0.1, linewidth= 1) #generates a plot of the results in real-time.
PRT.start() #starts real-time plotting.
log.info('Setting-up the Worker.')
W =Worker(results) #worker object to run said procedure
W.start() #starts the worker
W.join(timeout=3600) #joins the worker back to the current thread and waits 1 hour (3600 seconds) for it to stop. 
data = Plot.Measurement(W)

           