

import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from skn.query import Query
from skn.CAN.fields.channels import *
from skn.CAN.tags.tags import *

print('Loading data')
dataframe = pd.read_csv('FSG_data_PU.csv')
#Iterate thru the columns and remove nan values
print('Data loaded')


def main():
    #plot_cells_and_SoC()
    print(' Calculating SoC in car For FSG')
    print("|******************************|")
    SoC_in_car()
    #print(' Calculating SoC in car For FSE')
    #print("|******************************|")
    #global dataframe
    #dataframe = pd.read_csv('FSE_data.csv')
    #SoC_in_car()
    print('Done')

def plot_cells_and_SoC():
    fig, axs = plt.subplots(1, 2, figsize=(20, 20))
    
    axs[0].plot(dataframe['time'], dataframe['StateOfCharge_counted_coloumbs'])
    #axs[0].plot(dataframe['time'], dataframe['StateOfCharge_soc_lut_filtered'])
    axs[0].set_title('State of Charge')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('State of Charge')
    
    cell = 0
    for i in tqdm(range(0, 1), desc='Plotting Segments'):
        for j in tqdm(range(0, 12), desc='Plotting Cells', leave=False):
            axs[1].plot(dataframe['time'], dataframe[f'Voltages_S{i}_cell_{cell:03}'])
            cell +=1
    axs[1].set_title('Cell Voltages')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Voltage')
    
    plt.show()
    

    
def SoC_count_current(prev_current, current, period):
    #Use high pressision trapzoidal rule to calculate the SoC count current
    integrated_current = 1/2 * period * (current - prev_current) + period * current
    return integrated_current
    
def Improved_SoC_count_current(prev_current, current, period):
    integrated_current = 1/2 * period * (current - prev_current) + period * current
    #acount for current consumbed by internal losses
    R_i = 0.1209
    Correction = integrated_current * R_i
    integrated_current += Correction

    return integrated_current
    
def soc_convert_percent_to_coulomb_count(SoC):
    #Convert the SoC to coulomb count
    battery_capacity = 13.4 * 3600  #((6806 * 2) / 1000) * 3600
    return (1-(SoC/100)) * battery_capacity

def convert_coulomb_count_to_SoC(coulomb_count):
    #Convert the coulomb count to SoC
    battery_capacity = 13.4 * 3600  #((6806 * 2) / 1000) * 3600
    return (1-(coulomb_count/battery_capacity))*100

def plot_columbs_and_SoC(coulomb_count_python_math, coulomb_count_python_math_imp):
    SoC_counted_coloumbs = dataframe['ams.StateOfCharge.counted_coloumbs'].values
    SoC_soc_lut_filtered = dataframe['ams.StateOfCharge.soc_lut_filtered'].values
    SoC_coulombs = dataframe['ams.StateOfCharge.soc'].values
    
    SoC_counted_coloumbs = SoC_counted_coloumbs[:-1]
    SoC_soc_lut_filtered = SoC_soc_lut_filtered[:-1]
    SoC_coulombs = SoC_coulombs[:-1]
    
    time = dataframe['timestamp']
    time = time[:-1]
    
    #two subplots one for SoC and the other for the coulomb count
    fig, axs = plt.subplots(2, 1, figsize=(20, 20))
    axs[0].plot(time, SoC_counted_coloumbs, label='AMS.SoC counted Coulomb')
    axs[0].plot(time, coulomb_count_python_math, label='Py.SoC counted Coulomb')
    axs[0].plot(time, coulomb_count_python_math_imp, label='Py.SoC Improved counted Coulomb')
    axs[0].set_title('Coulomb Count Compare')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Coulomb Count')
    axs[0].legend()
    
    soc_py = []
    soc_py_imp = []
    soc_corr = []
    corr = dataframe['ams.StateOfCharge.counted_coloumbs'].values[1] - soc_convert_percent_to_coulomb_count(92)
    
    for i in tqdm(range(0, len(coulomb_count_python_math))):
        soc_py.append(convert_coulomb_count_to_SoC(coulomb_count_python_math[i]))
        soc_py_imp.append(convert_coulomb_count_to_SoC(coulomb_count_python_math_imp[i]))
        soc_corr.append(convert_coulomb_count_to_SoC(soc_convert_percent_to_coulomb_count(SoC_coulombs[i]) - corr))
    
    axs[1].plot(time, SoC_soc_lut_filtered, label='AMS.SoC lut filtered')
    axs[1].plot(time, SoC_coulombs, label='AMS.SoC Coulomb')
    axs[1].plot(time, soc_corr, label='AMS.SoC Coulomb corrected')
    axs[1].plot(time, soc_py, label='Py.SoC counted Coulomb')
    axs[1].plot(time, soc_py_imp, label='Py.SoC Improved counted Coulomb')
    axs[1].set_title('State of Charge Compare')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('State of Charge')
    axs[1].legend()
    
    plt.show()
    

def SoC_in_car():
    print('SoC in car calculation:')
    #Use high pressision trapzoidal rule to calculate the SoC in the car
    coulomb_count = soc_convert_percent_to_coulomb_count(84)
    improved_count = soc_convert_percent_to_coulomb_count(92) 
    coulomb_count_car = dataframe["ams.StateOfCharge.counted_coloumbs"].values[-1]
    
    ts_current = dataframe['ams.TSData.current_raw']
    _37V_current = dataframe["ccc.CurrentMeasure.current_37V5"]
    time = dataframe['timestamp'] 
    
    factor_fixed = 0.06
    battery_capacity = 13.4 * 3600  #((6806 * 2) / 1000) * 3600
    factor = (dataframe["ams.TSData.voltage_ts"].values / 600) * (0.06)
    
    coulomb_count_python_math = []
    coulomb_count_python_math_imp = []
    
    for i in tqdm(range(0, len(time)-1)):
        coulomb_count += SoC_count_current(ts_current.values[i], ts_current.values[i+1], time.values[i+1] - time.values[i])
        coulomb_count += SoC_count_current(_37V_current.values[i]*factor_fixed, _37V_current.values[i+1], time.values[i+1] - time.values[i])
        coulomb_count_python_math.append(coulomb_count)
        
        improved_count += Improved_SoC_count_current(ts_current.values[i], ts_current.values[i+1], time.values[i+1] - time.values[i])
        improved_count += Improved_SoC_count_current(_37V_current.values[i]*factor[i], _37V_current.values[i+1]*factor[i+1], time.values[i+1] - time.values[i])
        coulomb_count_python_math_imp.append(improved_count)
        
        
    SoC_Car = convert_coulomb_count_to_SoC(coulomb_count_car)    
    SoC_Py = convert_coulomb_count_to_SoC(coulomb_count)
    Soc_proposed = convert_coulomb_count_to_SoC(improved_count)    
    
    SoC_lut = dataframe['ams.StateOfCharge.soc_lut_filtered'].values[-1]
    SoC_Car_ac = dataframe['ams.StateOfCharge.soc'].values[-1]
    correction = dataframe['ams.StateOfCharge.counted_coloumbs'].values[1] - soc_convert_percent_to_coulomb_count(92)
    SoC_Car_corrected = convert_coulomb_count_to_SoC(coulomb_count_car-correction)
    
    print(f"State of Charge LUT:         {SoC_lut:20.6f}")
    print(f"Car AMS given SoC in car:    {SoC_Car_ac:20.6f}, error {(SoC_lut-SoC_Car_ac):6.2f}")
    print(f"Car calculated SoC in car:   {SoC_Car:20.6f}, error {SoC_lut-SoC_Car:6.2f}   {coulomb_count_car}")
    print(f"Car corrected SoC in car:    {SoC_Car_corrected:20.6f}, error {(SoC_lut-SoC_Car_corrected):6.2f}   diff: {coulomb_count_car-correction}")
    print(f"Python calculated SoC in car:{SoC_Py:20.6f}, error {(SoC_lut-SoC_Py):6.2f}   {coulomb_count}")
    print(f"Improved SoC in car:         {Soc_proposed:20.6f}, error {(SoC_lut- Soc_proposed):6.2f}   {improved_count}")
    plot_columbs_and_SoC(coulomb_count_python_math, coulomb_count_python_math_imp)


if __name__ == '__main__':
    main()