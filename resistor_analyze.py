###############################################################################################################
# Program Purpose: Analyze resistor data taken by Keithley 2450, experimentally confirm instrument specs.
#
# Author: Lindsay Spence (lindsay.spence@maine.edu) for the QPHT Lab in FIRST
#
# Created: 7/16/25
# Most Recent Update: 7/17/25
#
# Update Info: Added outlier exclusion with IQR method
#
###############################################################################################################

import pandas as pd 
import numpy as np 
import math
import matplotlib.pyplot as plt

# Stores list of all resistor .csv file prefixes to be looped through
resistances = ['220ohm', '560Ohm', '1kOhm', '4.7kOhm', '10kOhm', '1MOhm', '10MOhm']
for k in range(len(resistances)):
    processed = []

    # Loops through the 5 experiments with 10 data points each
    for i in range(1, 6):
        filename = f'./final_measurements/{resistances[k]}_Resistor_{i}.csv'
        df = pd.read_csv(
            filename,
            skiprows=9,
            names=['Iteration', 'Current(A)', 'Resistance (ohm)', 'Res. Stdev.']
        )

        # Calculates Percent Basic Accuracy for each data point
        df['Percent Basic Accuracy'] = df['Res. Stdev.'] / df['Resistance (ohm)'] * 100

        # Combines all 5 experiments into one csv file
        processed.append(df)
    data_df = pd.concat(processed, ignore_index=True)
    
    # Calculates the interquartile range (IQR) to find outliers in data
    q1 = data_df['Percent Basic Accuracy'].quantile(0.25)
    q3 = data_df['Percent Basic Accuracy'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5*iqr)
    upper_bound = q3 + (1.5*iqr)

    # Removes IQR outliers
    data_df = data_df[
        (data_df['Percent Basic Accuracy'] >= lower_bound) &
        (data_df['Percent Basic Accuracy'] <= upper_bound)
    ]

    # Determines average Percent Basic Accuracy for all experiments on one resistor
    avg_value = data_df['Percent Basic Accuracy'].mean()
    avg_df = pd.DataFrame([{
        'Iteration': 'AVERAGE',
        'Current(A)': '',
        'Resistance (ohm)': '',
        'Res. Stdev.': '',
        'Percent Basic Accuracy': avg_value
    }])

    # Adds average value to the bottom of csv and tells user it was successfully created
    df_with_avg = pd.concat([data_df, avg_df], ignore_index=True)
    df_with_avg.to_csv(f'Edited_{resistances[k]}_Resistor_all.csv', index=False)
    print(f"Appended average Percent Basic Accuracy = {avg_value:.4f}% to the {resistances[k]} CSV.")


