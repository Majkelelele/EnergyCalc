import pvlib
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from get_weather_data import get_irradiation_data


class PV:
    """
    A class to set up and run a PV system simulation using pvlib.
    
    Parameters provided in the constructor include location settings, 
    PV module/inverter specifications, system configuration, and data retrieval parameters.
    """
    def __init__(self,
                 surface_tilt: float,
                 surface_azimuth: float,
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


class PVModel:
    def __init__(self, 
            pv_models: [PV],
            latitude: float,
            longitude: float,
            tz: str,
            altitude: float,
            data_start: int = 2023,
            data_end: int = 2023,
            data_date_for_ac: str = "2023-07-01",
            csv_output_path: str = 'backend/data/ac_power_15min.csv',
            resample_freq: str = '15min'):

        """
        Initializes the PV system simulation.
        """
        
        # Set up location
        self.location = Location(latitude=latitude, longitude=longitude, tz=tz, altitude=altitude)

        # Create ModelChain instances with the systems and location
        self.model_chains = [ModelChain(system=model.system, location=self.location) for model in pv_models]
        
        # Data retrieval and processing parameters
        self.data_start = data_start
        self.data_end = data_end
        self.data_date_for_ac = data_date_for_ac
        self.csv_output_path = csv_output_path
        self.resample_freq = resample_freq

        # Calculate the AC output in 15 min intervals
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
        Processes the AC power output data for a specific date by resampling and interpolating,
        then saves the results to a CSV file.
        """
        # Extract AC power series for the specified date
        
        self.__run_models()

        ac_series = sum(modelchain.results.ac.loc[self.data_date_for_ac] for modelchain in self.model_chains)
        
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
        # Save the processed data to CSV
        self.ac_series.to_csv(self.csv_output_path, index_label='timestamp')

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
        # self.save_ac_data()
        self.plot_ac_data()
        

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
        data_start=2023,
        data_end=2023,
        data_date_for_ac="2023-07-01",
        csv_output_path='../../data_months/solar_energy/ac_pv.csv',
        resample_freq='15min',
        pv_models = [pv_model]
    )
    
    # Run the model, process the data, and plot (if desired)
    pv_system.run_all()
