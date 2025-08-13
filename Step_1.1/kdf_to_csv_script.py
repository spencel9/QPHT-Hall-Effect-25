import pandas as pd
import matplotlib.pyplot as plt

###############################
# NOTE:
# This code will only operate as is with prexisting folder and
# only on Windows. To make this code compatiable with Mac, simply
# replace all '\' in filename with '/' --> A small but costly mistake.
################


#########################################
# Change these values ONLY
num_files_plus_1 = 4 ### Only did 3 trials for most of the resistors
resistor_list = ['220Ohm', '560Ohm', '1kOhm', '4.7kOhm', '10kOhm']
resistor_val = '220Ohm'

#########################################
for i in range (0, len(resistor_list)):
    resistor_val = resistor_list[i]
    for n in range(1, num_files_plus_1):
        
        ####### For Mac
        filename = f"./Delta Mode Exp/Test_{n}_{resistor_val}.kdf"  #Delta Mode Exp\Test_1_1MOhm.kdf

        ####### For Windows
        #filename = f".\Delta Mode Exp\Test_{n}_{resistor_val}.kdf"  #Delta Mode Exp\Test_1_1MOhm.kdf

        data_df = pd.read_csv(filename, skiprows=1, sep = r'\s+', names=['Points', 'Time', 'Resistance', 'Delta Voltage', 'Conductance', 'Power'])
        data_df.to_csv(filename[:-4])

        plt.scatter(data_df['Time'], data_df['Resistance'])
        plt.xlabel('Time (s)')
        plt.ylabel('Resistance (Ohms)')
        plt.title(f'Measured Delta Mode Resistance for {resistor_val} Resistor')
        plt.grid(True)

        ######### For Mac
        plt.savefig(f'./Delta Mode Exp/Figs/Test_{n}_{resistor_val}.png')

        ######### For Windows
        #plt.savefig(f'.\Delta Mode Exp\Figs\Test_{n}_{resistor_val}.png')

        plt.show()
        plt.close()
   

