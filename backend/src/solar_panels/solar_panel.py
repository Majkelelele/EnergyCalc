class SolarPanel:
    def __init__(self, capacity_kw, efficiency=0.85, tilt_angle=30, orientation='south'):
        """
        Initialize the solar panel system.
        
        :param capacity_kw: Total capacity of the solar panel system (kW)
        :param efficiency: Efficiency of the solar panel system (default: 85%)
        :param tilt_angle: Tilt angle of the panels (default: 30 degrees)
        :param orientation: Orientation of the panels (default: south-facing)
        """
        self.capacity_kw = capacity_kw
        self.efficiency = efficiency
        self.tilt_angle = tilt_angle
        self.orientation = orientation

    def estimate_production(self, peak_sun_hours, weather_factor=1.0):
        """
        Estimate daily energy production based on average peak sun hours and weather conditions.
        
        :param peak_sun_hours: Average peak sun hours for the day
        :param weather_factor: Adjustment factor for weather conditions (1.0 = perfect weather)
        :return: Estimated energy production in kWh
        """
        return self.capacity_kw * peak_sun_hours * self.efficiency * weather_factor

    def forecast_daily_production(self, sun_hours_forecast):
        """
        Forecast hourly energy production based on a given sun hours forecast.
        
        :param sun_hours_forecast: List of hourly sun irradiance factors (e.g., [0.1, 0.3, ...])
        :return: List of hourly production in kWh
        """
        hourly_production = [
            self.capacity_kw * hour_sun * self.efficiency for hour_sun in sun_hours_forecast
        ]
        return hourly_production

    def get_real_time_production(self, current_irradiance, max_irradiance=1000):
        """
        Calculate real-time energy production based on current solar irradiance.
        
        :param current_irradiance: Current solar irradiance (W/m²)
        :param max_irradiance: Maximum possible irradiance for full capacity (default: 1000 W/m²)
        :return: Real-time energy production in kW
        """
        irradiance_factor = current_irradiance / max_irradiance
        return self.capacity_kw * irradiance_factor * self.efficiency
