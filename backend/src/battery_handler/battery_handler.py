from battery_handler.consts import DEFAULT_VOLTAGE, DEFAULT_AMPERAGE

# https://pybamm.org/
# library for simulating batteries TODO

class Battery:
    def __init__(
            self, 
            price: float,
            capacity: int, 
            DoD: float, 
            efficiency: float,
            life_cycles: int,
            is_grant_reduction: bool = False,
            charge_level: float = 0.0,
            socket_amperage: int = DEFAULT_AMPERAGE,
            socket_voltage: int = DEFAULT_VOLTAGE,

            ):
        self.price = price
        self.capacity = capacity
        self.grant_reduction = self.price * 0.5 if is_grant_reduction else 0

        # Battery current charge level in kWh
        self.charge_level = charge_level

        # Depth of Discharge (DoD) is the fraction of the battery that is
        # discharged relative to the overall capacity of the battery.
        self.DoD = DoD

        self.socket_amperage = socket_amperage
        self.socket_voltage = socket_voltage

        # Socket power output in kW (socket that we plugged the battery in)
        self.socket_power_output = (socket_amperage * socket_voltage) / 1000

        # The battery charging efficiency is the ratio between the energy 
        # consumed by the charging process and saved battery energy.
        # e.g. 0.9 means 90% efficiency
        self.efficiency = efficiency

        self.charging_time = self.__charging_time()

        # The battery life cycles. The number of cycles a battery can undergo 
        # is directly related to its lifespan. After this number of cycles,
        # the battery capacity will drop (for example to  80% of its original capacity).
        self.life_cycles = life_cycles
        
        # adding life_cycles of reduced efficiency
        self.cost_per_cycle = (self.price - self.grant_reduction)/ (self.life_cycles + 0.25 * self.life_cycles)
        # how many kwh can be charged per hour
        self.charging_per_hour = self.__calculate_charging_per_hour()

    def get_expected_month_cycles(self):
        return (self.life_cycles + 0.25 * self.life_cycles) / 30
    
    def set_grant(self, grant):
        self.grant_reduction = self.price * 0.5 if grant else 0

    def get_real_price(self) -> float:
        return self.price - self.grant_reduction
        
    def __charging_time(self) -> float:
        # shouldnt this be capacity * DOD - charge_level? TODO
        return round(((self.capacity - self.charge_level) * self.DoD) \
                / (self.socket_power_output * self.efficiency),3)

    def __max_charging_time(self) -> float:
        return (self.capacity * self.DoD) \
                / (self.socket_power_output * self.efficiency)

    
    def __calculate_charging_per_hour(self) -> float:
        # shouldnt we multiply capacity by DOD? TODO
        return round(self.capacity / self.__max_charging_time(),3)

    def one_cycle_cost(self):
        return  round(self.cost_per_cycle,3)
    
    def one_kwh_cost(self):
        return round(self.cost_per_cycle / self.capacity, 3)

    def charging_per_segment(self):
        return round(self.charging_per_hour / 4, 3)
    def __str__(self):
        return (f"Battery(price={self.get_real_price()}, capacity={self.capacity}, "
                f"efficiency={self.efficiency}, life_cycles={self.life_cycles}, "
                f"grant_reduction={self.grant_reduction})")
