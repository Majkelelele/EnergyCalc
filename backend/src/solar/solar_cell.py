import pvlib
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import matplotlib.pyplot as plt
from solar.get_weather_data import get_irradiation_data
import numpy as np

class SolarPanel:
    def __init__(self, efficiency, area, sunlight_hours, latitude, longitude):
        """
        Initializes a SolarPanel instance.
        :param efficiency: Efficiency of the panel (0 to 1).
        :param area: Area of the panel in square meters.
        :param sunlight_hours: Average sunlight hours per day.
        :param latitude: Latitude coordinate of the panel location.
        :param longitude: Longitude coordinate of the panel location.
        """
        self.efficiency = efficiency
        self.area = area
        self.sunlight_hours = sunlight_hours
        self.latitude = latitude
        self.longitude = longitude
        self.solar_constant = 1000  # Average solar power per m² in W
    
    def daily_energy_output(self):
        """
        Calculates the daily energy output in kWh.
        """
        energy = self.efficiency * self.area * self.solar_constant * self.sunlight_hours / 1000
        return energy
    
    def yearly_energy_output(self):
        """
        Calculates the yearly energy output in kWh.
        """
        return self.daily_energy_output() * 365
    
    def __str__(self):
        return (f"Solar Panel: {self.area} m², Efficiency: {self.efficiency*100}%, Daily Output: {self.daily_energy_output():.2f} kWh, "
                f"Location: ({self.latitude}, {self.longitude})")


def save_solar_data(latitude = 52.20672318295605, longitude = 20.977651716685703,
                    date:str = '2023-03-01', path:str = "../../data_months/"):
    
    location = Location(latitude=latitude, longitude=longitude, tz="Europe/Berlin", altitude=112)
# specifications
    modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
    module = modules['Canadian_Solar_CS5P_220M___2009_']
    inverter = inverters['ABB__PVI_3_0_OUTD_S_US__208V_']

    temperature_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    system = PVSystem(surface_tilt=45,  # the inclination of the module's surface with respect to the horizontal surface
                    surface_azimuth=180,  # the angle between the South direction and the horizontal component of the surface normal
                    module_parameters=module,
                    inverter_parameters=inverter, 
                    temperature_model_parameters=temperature_params,
                    modules_per_string=8,
                    strings_per_inverter=2)

    modelchain = ModelChain(system=system, location=location)
    poa_data = get_irradiation_data(latitude=latitude, longitude=longitude, start=2023, end=2023)
    modelchain.run_model_from_poa(poa_data)
    ac_power = abs(round(modelchain.results.ac / 1000, 3))
    ac_power_march = ac_power[date].values / 4
    ac_power_march = np.repeat(ac_power_march, 4)
    pd.DataFrame(ac_power_march).to_csv(path + f"ac_power_15min_{date}.csv", index=False)

# save_solar_data(date = "2023-08-01")