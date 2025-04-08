from backend.src.battery_handler.battery_handler import Battery
import numpy as np

def fill_quarters_G12(val1, val2):
# val2 > val1, so val2 is the more expensive part of the day
    arr = np.full(96, val2)

    # 00:00 to 06:00 => indices 0 to 23
    arr[0:24] = val1

    # 13:00 to 15:00 => indices 52 to 59
    arr[52:60] = val1
    arr[88:] = val1

    return arr

def fill_quarters_G13(val1, val2, val3):
# val2 > val1, and val3 > val2
    arr = np.full(96, val1)

    # 7am to 13 val2
    arr[28:52] = val2

    # 19-22 val3
    arr[76:88] = val3

    return arr

TOL = 0.05
SIZE = 96
# aktualna na dzień poboru energii stawka podatku akcyzowego (zł/kWh); aktualna stawka podatku akcyzowego wynosi 5 zł/MWh;
CURRENT_A = 5 / 1000

# 0,095 zł/kWh (składnik kosztowo-marżowy, w tym koszty bilansowania handlowego);
B_ENEA = 0.095
K_PGE = 0.0812
SC_TAUTRON = 0.0892
Wk_ENERGA = 0.108

VAT = 0.23

ENEA_MONTHLY_COST = 9.99
ENERGA_MONTHLY_COST = 9.99
PGE_MONTHLY_COST = 49.90
TAURON_MONTHLY_COST = 0


PGE_STATIC_KWH = 0.62
ENEA_STATIC_KWH = 0.62
TAURON_STATIC_KWH = 0.62
ENERGA_STATIC_KWH = 0.62

ENEA_MONTHLY_COST_STATIC = 0
ENERGA_MONTHLY_COST_STATIC = 0
PGE_MONTHLY_COST_STATIC = 0
TAURON_MONTHLY_COST_STATIC = 0

PGE_MIN_PRICE_CAP = 0
TAURON_MIN_PRICE_CAP = 0.005

ADDITIONAL_HELPER_SELLING = 1.23

# TODO G13 sligthly different for summer and winter 
# https://akademia-fotowoltaiki.pl/tauron/#:~:text=Taryfa%20G13%20%E2%80%93%20taryfa%20przedpo%C5%82udniowa%20(%C5%9Brednia,%E2%80%93%207.00%2C%20a%20tak%C5%BCe%20weekendy

# G14_TAURON
G13_TAURON = fill_quarters_G13(0.04,0.24, 0.42)
G12_TAURON = fill_quarters_G12(0.08, 0.36)
G11_TAURON = np.full(SIZE, 0.32)

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