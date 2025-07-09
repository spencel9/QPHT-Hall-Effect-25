# Trial code from PyMeasure Doc on ManagedDocWindow

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import numpy as np
from time import sleep
from pymeasure.display.Qt import QtWidgets
from pymeasure.instruments.keithley import Keithley2450
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter

class LivePlottingPocedure(Procedure):

    # Locates the sourcemeter at the specified address
    SMU = Keithley2450('GPIB::18::INSTR', name= "SMU") 

    # Allows user to set values for the variables that appear on the UI
    iterations = IntegerParameter('Loop Iterations', units=None, minimum=1, maximum= 10000, step=None, default= 10)
    data_points = IntegerParameter('Data Points', units=None, minimum=10, maximum= 10000, step=None, default= 10)
    delay = FloatParameter('Delay Time', units='s', default=0.1)
    I_max = FloatParameter('Current Max', units='A', minimum= 0, maximum= 105, decimals= 15, default = 1e-3)
    I_min = FloatParameter('Current Min', units='A', minimum= -105, maximum= 1e-15, decimals= 15, default= -1e-3)
    
    # Makes a separate variable the is Python int/float NOT PyMeasure int/float (like above)
    iterations1 = int(str(iterations))
    data_points1 = int(str(data_points))
    I_max1 = float(str(I_max)[:-2])
    I_min1 = float(str(I_min)[:-2])

    # Create arrays for all the data from the iterations
    data_ar = np.linspace(I_min1, I_max1, num = iterations1) # Array that store all current step values
    curr_ar = [] # Current array
    res_ar = np.zeros((len(data_ar), iterations1))   # Resistance array for each measurement
    avg_res_ar = [] # Average resistance array
    sigma_res_ar = [] # Standard deviation of average resistance array

    # Global variable that is NECESSARY for PyMeasure to work (I think). Needs to match output data (where it 'emits' the data)
    DATA_COLUMNS = ['Iteration', 'Current (A)', 'Resistance (ohm)', 'Resistance Stdev']

    # Method to start the measurements from the connected device (Keithley 2450)
    def start_measure(self):
        
        self.SMU.use_front_terminals() #instructs the sourcemeter to measure from the front terminals
        self.SMU.reset() #resets the sourcemeter current and voltage to zero.
        self.SMU.apply_current() #informs the sourcemeter to act as a current source.
        self.SMU.wires = 4 #Sets the Sourcemeter to 4-wire mode so that a 4-probe measurement can be made.
        self.SMU.compliance_voltage = 100
        self.SMU.source_current_range = self.I_max #sets the voltage range to 20 V.
        self.SMU.measure_resistance() #informs the sourcemeter to measure resistance.
        self.SMU.enable_source() #enables the SMU to act as a source of current through the sample.

    # Method from example code I'm scared to delete, reports to Experiment Log though
    def startup(self):
        log.info("Setting up the Keithley 2450 for measuring resistance...")

    # Method the executes the actual experiment
    def execute(self):

        # Writes this line to the Experiment Log
        log.info("Starting the loop of %d iterations" % self.iterations)
        i = 0 # Re-initalize variable for continuous use functionality
        for i in range(self.iterations):
            
            # Collects the value of the current for this iteration and permanately store value in pre-existing array
            temp_curr = self.data_ar[i]
            self.curr_ar = np.append(self.curr_ar, [temp_curr])

            # Communicates with instrument to start measuring and to increase the source meter to the next current
            self.start_measure()
            self.SMU.ramp_to_current(temp_curr,steps= 10, pause= 1e-3) #ramps the sourcemeter to the next current

            # Collects the value of the Resistance (throug Voltage) for this iteration, takes the average value, then permanately store value in pre-existing array
            for j in range(self.iterations):
                self.res_ar[i, j] = self.SMU.resistance #measures the voltage at the set current
            temp_res = np.mean(self.res_ar[i,:])
            self.avg_res_ar = np.append(self.avg_res_ar, [temp_res])

            # Takes the standard deviation of the measured resistance array for this iteration then permanetloy stores to a pre-existing array
            temp_sig = np.std(self.res_ar[i,:])
            self.sigma_res_ar = np.append(self.sigma_res_ar, [temp_sig])

            # The number of items in 'data' below must match the number of items in 'DATA_COLUMNS'
            data = {
                'Iteration': i,
                'Resistance (ohm)': temp_res,
                'Current (A)': temp_curr,
                'Resistance Stdev': temp_sig
            }

            # Output to Experiment Log, created csv and UI
            self.emit('results', data) # Output to Experiment Log
            log.debug("Emitting results: %s" % data) # Output to Experiment Log
            self.emit('progress', 100 * i / self.iterations) # Outputs as progress bar to UI
            sleep(self.delay) # Lets the experiment take a little break (can delete if you want)
            
            # Stops the experiment if it encounters and error or the 'Abort' button is used
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break


######################################################
#  Notes about the Managed Dock Window
#
#  - Can move Docks around by dragging and dropping the blue Dock banner
#  - Can make multiple figures appear in the same space by dragging one figure to
#    the center of another figure to create a tab
#  - Can save Dock layout by right-clicking on the blue Dock banner and selecting
#    'Save Dock Layout'
#      - Note: Be careful with saving layouts, could result in an error not letting
#        you run the program. Fix: delete the .json file and redo desired layout.
#  - Can make a plot pop out of the main UI by double-clicking the blue Dock banner
#    and return to the original layout by clicking the 'X' in the top right corner
#    of the pop-up figure window.

#####################################################

class MainWindow(ManagedDockWindow):

    def __init__(self):
        super().__init__(
            procedure_class=LivePlottingPocedure, # Please don't touch this line.

            inputs=['iterations', 'delay', 'data_points', 'I_max', 'I_min'], ## Variables that user can change via UI
            displays=['iterations', 'delay', 'data_points', 'I_max', 'I_min'],   ## Must match the inputs array (I think lol)

            # If you want to increase the number of plots show in the UI, add another named variable to either list below
            x_axis=['Current (A)', 'Resistance (ohm)'],  ## Variables that are avaliable to plot on x-axis
            y_axis=['Current (A)', 'Resistance (ohm)']  ## Variables that are avaliable to plolt on y-axis
        )
        self.setWindowTitle('Keithley 2450 4-Wire Resistance GUI - v1.0')  ## Name of GUI Application


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())