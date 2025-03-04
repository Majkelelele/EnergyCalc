from solar.solar_cell import SolarPanel
from backend.scripts.making_data_script import generate_energy_usage_200days

def api_call(daily_usage:float, company:str, grant_applicable:bool, solar:SolarPanel):
    
    generate_energy_usage_200days(total_usage=daily_usage)
