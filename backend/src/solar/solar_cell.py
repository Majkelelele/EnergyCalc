import pvlib
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import matplotlib.pyplot as plt
from get_weather_data import get_irradiation_data
import numpy as np

# Define location (example: Adolfa Pawińskiego, Poland)
latitude, longitude = 52.20672318295605, 20.977651716685703
location = Location(latitude=latitude, longitude=longitude, tz="Europe/Berlin", altitude=112)

# Retrieve module and inverter specifications
modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
module = modules['Canadian_Solar_CS5P_220M___2009_']
inverter = inverters['ABB__PVI_3_0_OUTD_S_US__208V_']

# Define temperature model parameters
temperature_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Define PV system
system = PVSystem(surface_tilt=45,  # the inclination of the module's surface with respect to the horizontal surface
                  surface_azimuth=180,  # the angle between the South direction and the horizontal component of the surface normal
                  module_parameters=module,
                  inverter_parameters=inverter, 
                  temperature_model_parameters=temperature_params,
                  modules_per_string=8,
                  strings_per_inverter=2)

# Create a ModelChain instance
modelchain = ModelChain(system=system, location=location)

# Retrieve POA (plane-of-array) data from external source
poa_data = get_irradiation_data(latitude=latitude, longitude=longitude, start=2023, end=2023)

# Run the model
modelchain.run_model_from_poa(poa_data)

# Extract the AC power output data (in watts)
ac_power = abs(round(modelchain.results.ac / 1000, 3))

# Resample to 15-minute intervals
# ac_power_15min = ac_power.resample('15T').sum()  # Sum the power over each 15-minute period

# Interpolate missing values (if any) to avoid NaN values in the time series
# ac_power_15min_interpolated = ac_power_15min.interpolate(method='time')

# Calculate total energy output in kWh for the entire period (sum of 15-minute periods)
# total_energy_kWh = ac_power.sum() # Convert from watts to kilowatts (divide by 1000)

ac_power_march_1 = ac_power['2023-03-01'].values / 4
ac_power_march_1 = ac_power_march_1, 4

print(ac_power_march_1)
# Print total energy output
print(f"Total energy output: {ac_power_march_1.sum():.2f} kWh")

# Save the interpolated 15-minute data to a CSV file
# ac_power_march_1.to_csv('ac_power_15min.csv', index=False)
