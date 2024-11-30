import pvlib

from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

import pandas as pd

import matplotlib.pyplot as plt

from get_weather_data import get_irradiation_data



# Define location (example: Adolfa Pawińskiego, Poland)
latitude, longitude = 52.20672318295605, 20.977651716685703
location = Location(latitude=latitude, longitude=longitude, tz="Europe/Berlin", altitude=112)

# Retrieve module and inverter specifications
# retrieve_sam(path=...) # The original library only contains modules and inverters from up to 2019, this library contains newer ones
modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
module = modules['Canadian_Solar_CS5P_220M___2009_']
inverter = inverters['ABB__PVI_3_0_OUTD_S_US__208V_']

# Define temperature model parameters
temperature_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

# Define PV system
system = PVSystem(surface_tilt=45, # the inclination of the module's surface with respect to the horizontal surface
                  surface_azimuth=180, # the angle between the South direction and the horizontal component of the surface normal
                  module_parameters=module,
                  inverter_parameters=inverter, temperature_model_parameters=temperature_params,
                  modules_per_string=10,
                  strings_per_inverter=7)

# Create a ModelChain instance
modelchain = ModelChain(system=system, location=location)

# Retrieve POA data
poa_data = get_irradiation_data(latitude=latitude, longitude=longitude, start=2023, end=2023)

# Run the model
modelchain.run_model_from_poa(poa_data)

# Plot the results
# modelchain.results.ac.plot(figsize=(15, 5), title='PV System Output (AC Power)', ylabel='AC Power (W)', xlabel='Time')
# plt.show()
# Extract 'ac' data for July 1st, 2023
ac_series = modelchain.results.ac.loc["2023-07-01"]

# Define the start and end times based on the original Series
start_time = ac_series.index.min()
end_time = ac_series.index.max() + pd.Timedelta(minutes=45)

# Create a new datetime index with 15-minute frequency
new_index = pd.date_range(start=start_time, end=end_time, freq='15min', tz=ac_series.index.tz)

# Reindex the original Series to the new 15-minute index
ac_15min = ac_series.reindex(new_index)

# Interpolate missing values using 'time' method
ac_15min_interpolated = ac_15min.interpolate(method='time')

# Save the interpolated 15-minute data to a CSV file
ac_15min_interpolated.to_csv('backend/data/ac_power_15min.csv', index_label='timestamp')





