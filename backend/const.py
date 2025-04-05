from backend.src.battery_handler.battery_handler import Battery

TOL = 0.05
SIZE = 96
# aktualna na dzień poboru energii stawka podatku akcyzowego (zł/kWh); aktualna stawka podatku akcyzowego wynosi 5 zł/MWh;
CURRENT_A = 5 / 1000

# 0,095 zł/kWh (składnik kosztowo-marżowy, w tym koszty bilansowania handlowego);
B_ENEA = 0.095
K_PGE = 0.0812
SC_TAUTRON = 0.892
Wk_ENERGA = 0.108

VAT = 0.23

ENEA_MONTHLY_COST = 18.45
ENERGA_MONTHLY_COST = 9.99
PGE_MONTHLY_COST = 49.90
TAURON_MONTHLY_COST = 0



PGE_STATIC_KWH = 1.10
ENEA_STATIC_KWH = 1.10
TAURON_STATIC_KWH = 0.77
ENERGA_STATIC_KWH = 0.76
ENEA_MONTHLY_COST_STATIC = 0
ENERGA_MONTHLY_COST_STATIC = 0
PGE_MONTHLY_COST_STATIC = 0
TAURON_MONTHLY_COST_STATIC = 0

PGE_MIN_PRICE_CAP = 0
TAURON_MIN_PRICE_CAP = 0.005

BATTERIES = [
        Battery(
        price=4800, 
        capacity=2.88, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=6000,
        grant_reduction=True
    ),
    Battery(
        price=8000, 
        capacity=5.18, 
        DoD=0.95, 
        efficiency=0.98, 
        life_cycles=4000,
        grant_reduction=True
    ),
    Battery(
        price=14350, 
        capacity=10.36, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=4000,
        grant_reduction=True
    ),
    ]