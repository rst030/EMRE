"""Experiment file for a potential series at the Magnettech MS5000 for different temperatures"""
#
# Structure last edited: 2022-02-22
#
# adjust the parameters for the planned measurement in this file and reference it when running the main gui script
# follow the instructions in the following section to setup everything necessary outside of pythen
#
#
# Manual for operation with the ESR studio software:
#-----------------------------------------------------------
#
# 1. Folder Structure:
# - If not existing, ESR studio will generate the directory 'Potential Series' with the subdirectories 'Cooled_spectra' and 'RT_spectra'
#   after acquiring the first spectra for the respective temperatures
# - Existing files of the form '*dummy.xls' in the 'Potential Series' are counted before the measurement and do not have to be deleted before
#
# 2. Hotkey:
# - Make sure the script '...' from the Desktop is running before starting the measurement
#
# 3. Set up the cwEPR parameters:
# - In ESR studio in the tab 'Recipe Editor' you will find the recipe 'pot_step_RT' and 'pot_step_cooled'. Change the cwEPR settings there to setup the experiment and save the recipies.
#   The number of Scans for room temperature has to be at minimum 2. If you only care about the spectra after freezing, you do not have to change the 'pot_step_RT'.
# - If the sample is sensitive fields of 337mT or powers of 0.01mW you have to adjust the recipe 'pot_RT_dummy'!
#
# 4. Set up the temperature parameters:
# - In ESR studio in the tab 'Sequence Editor' you will find the sequences 'Unnamed' and 'Mundane', where the former one is used for spectrums at RT and frozen and the latter
#   is used for only frozen spectra (it has the recipe 'pot_RT_dummy' already set up)
# - By editing the sequence and clicking to the first step 'Automated_...' you can access the parent parameters of the cycle and adjust the 'ambientT', 'coolT' and 'waittime'.
# - Save the sequence and check for errors. Leave the tab 'Sequence editor' open!
#
#
# Experiment Parameters:
#------------------------------------------------------------
# Duration for which the current transients are acquired
DURATIONOFTRANSIENTSEC = 10 # s
# Potential range of the series - cell is discharged to redPotential after each step
# lower limit
redPotential = 0 # V
# upper limit
oxPotential = 0 # V
# number of steps between redPotential and oxPotential - total measurement contains (2*nScans+1) steps
nScans = 1 # integer number
# Number of scans set for RT in ESR studio - needs to be consistent and at least 2!
scansPerStep = 2 # integer number
# Time for which the potentiostat keeps the potential after finishing the RT scans - adjust to stop either before or after freezing
keepPotTime = 30 # s




