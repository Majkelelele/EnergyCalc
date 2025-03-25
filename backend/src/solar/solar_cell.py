import pvlib
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from get_weather_data import get_irradiation_data


class PV:
    """
    A class to set up and run a PV system simulation using pvlib.
    
    Parameters provided in the constructor include location settings, 
    PV module/inverter specifications, system configuration, and data retrieval parameters.
    """
    def __init__(self,
                 surface_tilt: float = 45,
                 surface_azimuth: float = 180,
                 module_library: str = 'SandiaMod',
                 module_name: str = 'Canadian_Solar_CS5P_220M___2009_',
                 inverter_library: str = 'CECInverter',
                 inverter_name: str = 'ABB__PVI_3_0_OUTD_S_US__208V_',
                 modules_per_string: int = 8,
                 strings_per_inverter: int = 2,
                 temperature_model: str = 'open_rack_glass_glass'):

        """
        Initializes the PV system models.
        """

        # Retrieve module and inverter specifications
        modules = pvlib.pvsystem.retrieve_sam(module_library)
        inverters = pvlib.pvsystem.retrieve_sam(inverter_library)
        self.module = modules[module_name]
        self.inverter = inverters[inverter_name]
        
        # Define temperature model parameters from pvlib's TEMPERATURE_MODEL_PARAMETERS
        temperature_params = TEMPERATURE_MODEL_PARAMETERS['sapm'][temperature_model]
        
        # Define the PV system
        self.system = PVSystem(surface_tilt=surface_tilt,
                               surface_azimuth=surface_azimuth,
                               module_parameters=self.module,
                               inverter_parameters=self.inverter,
                               temperature_model_parameters=temperature_params,
                               modules_per_string=modules_per_string,
                               strings_per_inverter=strings_per_inverter)


import pandas as pd

class PVModel:
    def __init__(self, 
                 pv_models: [PV],
                 latitude: float,
                 longitude: float,
                 tz: str,
                 altitude: float,
                 data_date_range: tuple = ("2023-07-01", "2023-07-01"),
                 csv_output_path: str = '../../data/ac_power_15min.csv',
                 resample_freq: str = '15min'):
        """
        Initializes the PV system simulation.
        
        Parameters:
            pv_models (list): List of PV system models.
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            tz (str): Timezone.
            altitude (float): Altitude.
            data_date_range (tuple): A tuple of two date strings (start_date, end_date)
                                     for which AC power data is processed.
            csv_output_path (str): Path for the CSV output.
            resample_freq (str): Resampling frequency.
        """
        
        # Set up location
        self.location = Location(latitude=latitude, longitude=longitude, tz=tz, altitude=altitude)

        # Create ModelChain instances with the systems and location
        self.model_chains = [ModelChain(system=model.system, location=self.location) for model in pv_models]
        
        # Calculate data_start and data_end from data_date_range
        start_date, end_date = data_date_range
        start_year = pd.to_datetime(start_date).year
        end_year = pd.to_datetime(end_date).year
        
        # Assert that the years do not exceed 2023
        assert start_year >= 2018 and end_year <= 2023, "Data is available only till 2023."
        
        self.data_date_range = data_date_range
        self.data_start = start_year
        self.data_end = end_year
        self.csv_output_path = csv_output_path
        self.resample_freq = resample_freq

        # Calculate the AC output in specified intervals over the date range
        self.ac_series = self.__process_ac_data()

    def __run_models(self):
        """
        Retrieves irradiation data and runs the PV system model.
        """
        # Retrieve POA irradiation data using a helper function
        poa_data = get_irradiation_data(latitude=self.location.latitude,
                                        longitude=self.location.longitude,
                                        start=self.data_start,
                                        end=self.data_end)
        # Run the model from the plane-of-array data
        for model in self.model_chains:
            model.run_model_from_poa(poa_data)
    
    def __process_ac_data(self):
        """
        Processes the AC power output data for the specified date range by resampling and interpolating,
        then returns the processed series.
        """
        # Run the models to generate results
        self.__run_models()

        # Unpack the date range
        start_date, end_date = self.data_date_range
        
        # Extract AC power series for the specified date range from all model chains
        ac_series = sum(modelchain.results.ac.loc[start_date:end_date] for modelchain in self.model_chains)
        
        # Determine the start and end times for resampling (adding an extra 45 minutes for coverage)
        start_time = ac_series.index.min()
        end_time = ac_series.index.max() + pd.Timedelta(minutes=45)
        
        # Create a new datetime index at the specified frequency
        new_index = pd.date_range(start=start_time, end=end_time,
                                  freq=self.resample_freq,
                                  tz=ac_series.index.tz)
        
        # Reindex the AC series to the new index and interpolate missing values
        ac_resampled = ac_series.reindex(new_index)
        ac_interpolated = ac_resampled.interpolate(method='time')
        
        return ac_interpolated

    def save_ac_data(self):
        """
        Saves the processed AC power output data to a CSV file.
        """
        # Ensure the index is a datetime type
        if not pd.api.types.is_datetime64_any_dtype(self.ac_series.index):
            self.ac_series.index = pd.to_datetime(self.ac_series.index)
        
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.csv_output_path):
            os.makedirs(self.csv_output_path)
        
        current_date = None
        current_file = None
        
        # Iterate over each (timestamp, value) pair in the series
        for timestamp, value in self.ac_series.items():
            # Format the timestamp to get the date (YYYY-MM-DD)
            date_str = timestamp.strftime('%Y-%m-%d')
            
            # When the day changes, close the previous file (if open) and open a new one
            if date_str != current_date:
                if current_file is not None:
                    current_file.close()
                current_date = date_str
                filename = os.path.join(self.csv_output_path, f"{date_str}.csv")
                current_file = open(filename, 'w')
            
            # Write the value to the file, followed by a newline
            current_file.write(f"{round(value / 1000, 3)}\n")
        
        # Make sure to close the last file
        if current_file is not None:
            current_file.close()
        
        

    def plot_ac_data(self):
        """
        Plots the complete AC power output from the simulation.
        """
        plt.figure(figsize=(15, 10))
        self.ac_series.plot(title='PV System Output (AC Power)',
                            ylabel='AC Power (W)',
                            xlabel='Time')
        plt.show()
    
    def run_all(self):
        """
        Convenience method to run the model, process data, and optionally plot the results.
        """
        self.save_ac_data()
        # self.plot_ac_data()

def function_for_michal_zmyslony(
    *,
    # PV parameters
    surface_tilt: float = 45,
    surface_azimuth: float = 180,
    module_library: str = 'SandiaMod',
    module_name: str = 'Canadian_Solar_CS5P_220M___2009_',
    inverter_library: str = 'CECInverter',
    inverter_name: str = 'ABB__PVI_3_0_OUTD_S_US__208V_',
    modules_per_string: int = 4,
    strings_per_inverter: int = 1,
    temperature_model: str = 'open_rack_glass_glass',
    # PVModel parameters
    latitude: float = 52.20672318295605,
    longitude: float = 20.977651716685703,
    tz: str = "Europe/Berlin",
    altitude: float = 112,
    data_date_range: tuple = ("2023-07-01", "2023-07-01"),
    csv_output_path: str = '../../data',
    resample_freq: str = '15min'
):
    """
    Convenience function for Michal Zmyslony that creates a PV system and runs the simulation.
    
    It sets up the PV system with the given parameters, initializes the model, runs the simulation,
    and plots the AC power output.
    """
    # Create the PV system instance
    pv_instance = PV(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        module_library=module_library,
        module_name=module_name,
        inverter_library=inverter_library,
        inverter_name=inverter_name,
        modules_per_string=modules_per_string,
        strings_per_inverter=strings_per_inverter,
        temperature_model=temperature_model
    )
    
    # Create the PVModel instance
    pv_model_instance = PVModel(
        pv_models=[pv_instance],
        latitude=latitude,
        longitude=longitude,
        tz=tz,
        altitude=altitude,
        data_date_range=data_date_range,
        csv_output_path=csv_output_path,
        resample_freq=resample_freq
    )
    
    # Run the simulation (this will plot and save the AC power data)
    pv_model_instance.run_all()
    
    return pv_instance, pv_model_instance



# Example usage:
if __name__ == "__main__":
    # Create an instance with the desired parameters
    pv_model = PV(
        # module and inverter defaults are set as in the original code:
        surface_tilt=45,
        surface_azimuth=180,
        module_library='SandiaMod',
        module_name='Canadian_Solar_CS5P_220M___2009_',
        inverter_library='CECInverter',
        inverter_name='ABB__PVI_3_0_OUTD_S_US__208V_',
        modules_per_string=2,
        strings_per_inverter=8,
        temperature_model='open_rack_glass_glass',
    )
    pv_system = PVModel(
        latitude=52.20672318295605,
        longitude=20.977651716685703,
        tz="Europe/Berlin",
        altitude=112,
        data_date_range=("2023-07-01", "2023-07-01"),
        csv_output_path='../../data_months/solar_energy/ac_pv.csv',
        resample_freq='15min',
        pv_models = [pv_model]
    )
    
    # Run the model, process the data, and plot (if desired)
    # pv_system.run_all()
    
    function_for_michal_zmyslony(data_date_range=("2023-01-11", "2023-03-12"))
