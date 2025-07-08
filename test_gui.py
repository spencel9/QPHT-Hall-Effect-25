# Trial code from PyMeasure Doc on ManagedDocWindow

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
import numpy as np
import pandas as pd
from time import sleep
from pymeasure.display.Qt import QtWidgets
from pymeasure.instruments.keithley import Keithley2450
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter

class LivePlottingPocedure(Procedure):

    SMU = Keithley2450('GPIB::18::INSTR', name= "SMU") #locates the sourcemeter at the specified address

    ####################### IntegerParameter Error

    iterations = IntegerParameter('Loop Iterations', units=None, minimum=1, maximum= 10000, step=None, default= 10)
    iterations1 = int(str(iterations))
    data_points = IntegerParameter('Data Points', units=None, minimum=10, maximum= 10000, step=None, default= 10)
    #data_points = int(str(data_points1))
    delay = FloatParameter('Delay Time', units='s', default=0.1)
    #delay = float(str(delay1)[:-2])
    I_max = FloatParameter('Current Max', units='A', minimum= 0, maximum= 105, decimals= 15, default = 1e-3)
    I_max1 = float(str(I_max)[:-2])
    I_min = FloatParameter('Current Min', units='A', minimum= -105, maximum= 1e-15, decimals= 15, default= -1e-3)
    I_min1 = float(str(I_min)[:-2])
    

    data_df = pd.DataFrame(columns = ['Iterations', 'Current (A)', 'Voltage', 'Resistance (ohm)', 'Resistance Stdev'])
    data_df['Current (A)'] = np.linspace(I_min1, I_max1, num = iterations1)

    DATA_COLUMNS = ['Iteration', 'Current (A)', 'Resistance (ohm)', 'Resistance Stdev ']

    def startup(self):
        log.info("Setting up the Keithley 2450 for measuring resistance...")

        # All code below in this function provided by Ben Lichy
        self.SMU.use_front_terminals() #instructs the sourcemeter to measure from the front terminals
        self.SMU.reset() #resets the sourcemeter current and voltage to zero.
        #SMU.source_mode = 'current'

        self.SMU.use_front_terminals() #instructs the sourcemeter to measure from the front terminals
        self.SMU.reset() #resets the sourcemeter current and voltage to zero.
        self.SMU.apply_current() #informs the sourcemeter to act as a current source.
        self.SMU.wires = 4 #Sets the Sourcemeter to 4-wire mode so that a 4-probe measurement can be made.
        self.SMU.compliance_voltage = 100
        self.SMU.source_current_range = self.I_max #sets the voltage range to 20 V.
        self.SMU.measure_resistance() #informs the sourcemeter to measure resistance.
        self.SMU.enable_source() #enables the SMU to act as a source of current through the sample.


    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        
        for i in range(self.iterations):
            
            self.SMU.ramp_to_current(self.data_df.loc[i:'Current (A)'],steps= 10, pause= 1e-3) #ramps the sourcemeter to the next current

            for j in range(self.iterations):
              self.data_df.loc[j,'Voltage'] = self.SMU.resistance #measures the voltage at the set current
            self.data_df.loc[i, 'Resistance (ohm)'] = np.mean(self.data_df.loc['Voltage'][i:])
            self.data_df.loc[i, 'Resistance Stdev'] = np.std(self.data_df.loc['Voltage'][i:])
            
            # The number of items in 'data' below must match the number of items in 'DATA_COLUMNS'
            data = {
                'Iteration': i,
                'Resistance (ohm)': self.data_df.loc[i, 'Resistance (ohm)'],
                'Current (A)': self.data_df.loc[i, 'Current (A)'],
                'Resistance Stdev': self.data_df.loc[i, 'Resistance Stdev']
            }

            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break


class MainWindow(ManagedDockWindow):

    def __init__(self):
        super().__init__(
            procedure_class=LivePlottingPocedure,
            inputs=['iterations', 'delay', 'data_points', 'I_max', 'I_min'], ## Variables that user can change via UI
            displays=['iterations', 'delay', 'data_points', 'I_max', 'I_min'],   ## Must match the inputs array (I think lol)
            x_axis=['Iteration', 'Current (A)', 'Resistance (ohm)'],  ## Variables that are avaliable to plot on x-axis
            y_axis=['Current (A)', 'Resistance (ohm)']  ## Variables that are avaliable to plolt on y-axis
        )
        self.setWindowTitle('Keithley 2450 4-Wire Resistance GUI - v1.0')  ## Name of GUI Application


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())