import pvlib
import pandas as pd
from pvlib.location import Location
from pvlib.irradiance import get_total_irradiance
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

# Define location (example: Miami, FL)
latitude, longitude, tz = 25.7617, -80.1918, 'America/New_York'
location = Location(latitude, longitude, tz=tz)

# Define time range (1-day simulation)
times = pd.date_range('2024-11-09 00:00', '2024-11-09 23:59', freq='1H', tz=tz)

# Solar position and irradiance model
solar_position = location.get_solarposition(times)
clear_sky = location.get_clearsky(times)  # clear sky irradiance

# Define system parameters (example values)
module_parameters = {'pdc0': 240, 'gamma_pdc': -0.003}
temperature_model_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
surface_tilt, surface_azimuth = 30, 180  # Tilt and azimuth facing south

# Calculate irradiance on tilted panel
total_irradiance = get_total_irradiance(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    dni=clear_sky['dni'],
    ghi=clear_sky['ghi'],
    dhi=clear_sky['dhi'],
    solar_zenith=solar_position['apparent_zenith'],
    solar_azimuth=solar_position['azimuth']
)

# Estimate cell temperature
temperature = pvlib.temperature.sapm_cell(
    total_irradiance['poa_global'],
    temp_air=20,  # Example ambient temperature in °C
    wind_speed=1,  # Example wind speed in m/s
    **temperature_model_params
)

# Calculate DC output power
dc_power = pvlib.pvsystem.pvwatts_dc(
    total_irradiance['poa_global'],
    temperature,
    **module_parameters
)

# Battery parameters
battery_capacity = 5000  # Battery capacity in Wh (e.g., 5 kWh)
battery_soc = 0.5 * battery_capacity  # Initial SoC (50% of capacity)
charge_efficiency = 0.9  # 90% efficient charging
discharge_efficiency = 0.9  # 90% efficient discharging
soc_min = 0.2 * battery_capacity  # Minimum allowable SoC (20%)
soc_max = battery_capacity  # Max SoC (100%)

# Define hourly load demand in watts (example values, adjust as needed)
load_demand = [200, 250, 300, 400, 350, 250, 200, 100, 150, 200, 250, 300,
               350, 400, 450, 500, 400, 350, 300, 250, 200, 150, 100, 50]

battery_soc_history = [battery_soc]  # Track state of charge over time
battery_flow = []  # Track battery charge/discharge activity

for hour in range(24):
    solar_power = dc_power[hour]  # DC power generated from the solar array
    load_power = load_demand[hour]  # Power required by the load

    # Decision-making for power usage:
    if solar_power >= load_power:  # If solar power exceeds load demand
        # Use solar to meet load and charge the battery with excess
        battery_soc = min(battery_soc + (solar_power - load_power) * charge_efficiency, soc_max)
        battery_flow.append("Charging")
    else:
        # Solar is insufficient; cover the gap by discharging the battery
        energy_needed = (load_power - solar_power) / discharge_efficiency
        if battery_soc - energy_needed >= soc_min:
            battery_soc -= energy_needed
            battery_flow.append("Discharging")
        else:
            # Battery can't supply enough energy; load may not be fully met
            battery_soc = soc_min
            battery_flow.append("Battery Depleted")

    # Append battery state to history for plotting
    battery_soc_history.append(battery_soc)

# Output the battery state history to understand how it performed
print("Battery State of Charge Over 24 Hours:", battery_soc_history)
print("Battery Flow Activity:", battery_flow)

