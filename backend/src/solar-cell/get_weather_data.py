# PVGIS-SARAH3 is the default solar radiation dataset for Europe in the PVGIS tool

# TMY (typical meteorological year) - The data set has been produced by choosing for each month the most "typical" month out of the full time period available e.g. 16 years (2005-2023) for PVGIS-SARAH3. The variables used to select the typical month are global horizontal irradiance, air temperature, and relative humidity

# POA (plane of array) irradiance - measures the total solar radiation, including direct sunlight, diffuse light, and ground-reflected light, that is incident on the front surface of a PV module taking into account the tilt angle and orientation of the module

# POA data vs TMY data https://www.nrel.gov/docs/fy20osti/74768.pdf

import matplotlib.pyplot as plt
import pandas as pd
import pvlib.iotools

def get_irradiation_data(latitude, longitude, start, end):
  """
  Retrieve hourly solar irradiance data from PVGIS-SARAH3 for a given location 
  and time range.

  Parameters:
      latitude (float): Latitude of the location.
      longitude (float): Longitude of the location.
      start (int): Start year for the data range.
      end (int): End year for the data range.

  Returns:
      pd.DataFrame: A DataFrame containing calculated POA irradiance values:
          - poa_diffuse: Total diffuse irradiance on the tilted surface.
          - poa_global: Total global irradiance on the tilted surface.
  
  Notes:
      - The function uses PVGIS API to fetch solar data, specifically the SARAH3 dataset.
      - Typical Meteorological Year (TMY) data is stored in `backend/data/tmy_52.207_20.978_2005_2023.csv`.
      - Outputs can be visualized and saved to CSV for further analysis.

  Example:
      >>> get_irradiation_data(52.2067, 20.9777, 2005, 2023)
  
  References:
      - https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html
      - https://www.nrel.gov/docs/fy20osti/74768.pdf
  """
  
  poa_data, meta, inputs = pvlib.iotools.get_pvgis_hourly(
    latitude=latitude, longitude=longitude, 
    start=start, end=end,
    raddatabase="PVGIS-SARAH3",
    components=True,
    surface_tilt=45,
    surface_azimuth=0, # 0 is South in PVGIS
    outputformat='csv',
    usehorizon=True, userhorizon=None,
    pvcalculation=False, peakpower=None, pvtechchoice='crystSi', mountingplace='free', loss=0, trackingtype=0, optimal_surface_tilt=False, optimalangles=False, url='https://re.jrc.ec.europa.eu/api/', map_variables=True, timeout=30
  )

  poa_data["poa_diffuse"] = poa_data["poa_sky_diffuse"] + poa_data["poa_ground_diffuse"]
  poa_data["poa_global"] = poa_data["poa_direct"] + poa_data["poa_diffuse"]

  return poa_data