from backend.const import CURRENT_A, B_ENEA, VAT, ENEA_MONTHLY_COST, ENERGA_MONTHLY_COST, PGE_MONTHLY_COST, TAURON_MONTHLY_COST, K_PGE, SC_TAUTRON, Wk_ENERGA, ENEA_STATIC_KWH, PGE_STATIC_KWH, TAURON_STATIC_KWH, ENERGA_STATIC_KWH, ENEA_MONTHLY_COST_STATIC, ENERGA_MONTHLY_COST_STATIC, TAURON_MONTHLY_COST_STATIC, PGE_MONTHLY_COST_STATIC, SIZE, PGE_MIN_PRICE_CAP, TAURON_MIN_PRICE_CAP, G13_TAURON, G11_TAURON, G12_TAURON, ADDITIONAL_HELPER_SELLING
import numpy as np
import pandas as pd

def calculate_enea_prices(prices, sell_prices, tariff = "G11", static_prices=False):
    tarifs = 0
    if tariff == "G11":
        tarifs = G11_TAURON
    elif tariff == "G12":
        tarifs = G12_TAURON
    elif tariff == "G13":
        tarifs = G13_TAURON
    else:
        pass  # todo g14

    if static_prices:
        prices = np.full(SIZE, ENEA_STATIC_KWH) + tarifs
        return prices, sell_prices, ENEA_MONTHLY_COST_STATIC
    

    netto_prices = prices + CURRENT_A + B_ENEA
    buy_prices = netto_prices * (1 + VAT) + tarifs
    sell_prices = sell_prices * ADDITIONAL_HELPER_SELLING
    
    return buy_prices, sell_prices, ENEA_MONTHLY_COST


def calculate_energa_prices(prices, sell_prices, tariff = "G11", static_prices=False):
    tarifs = 0
    if tariff == "G11":
        tarifs = G11_TAURON
    elif tariff == "G12":
        tarifs = G12_TAURON
    elif tariff == "G13":
        tarifs = G13_TAURON
    else:
        pass  # todo g14

    if static_prices:
        prices = np.full(SIZE, ENERGA_STATIC_KWH) + tarifs
        return prices, sell_prices, ENERGA_MONTHLY_COST_STATIC
    
    netto_prices = prices + Wk_ENERGA
    buy_prices = netto_prices * (1 + VAT) + tarifs
    sell_prices = sell_prices * ADDITIONAL_HELPER_SELLING
    
    return buy_prices, sell_prices, ENEA_MONTHLY_COST

def calculate_pge_prices(prices, sell_prices, tariff = "G11", static_prices=False):
    tarifs = 0
    if tariff == "G11":
        tarifs = G11_TAURON
    elif tariff == "G12":
        tarifs = G12_TAURON
    elif tariff == "G13":
        tarifs = G13_TAURON
    else:
        pass  # todo g14

    if static_prices:
        prices = np.full(SIZE, PGE_STATIC_KWH) + tarifs
        return prices, sell_prices, PGE_MONTHLY_COST_STATIC
    
    prices = np.maximum(PGE_MIN_PRICE_CAP, prices) + tarifs
    netto_prices = prices + CURRENT_A + K_PGE
    buy_prices = netto_prices * (1 + VAT) + tarifs
    sell_prices = sell_prices * ADDITIONAL_HELPER_SELLING
    
    return buy_prices, sell_prices, PGE_MONTHLY_COST

def calculate_tauron_prices(prices, sell_prices, tariff = "G11", static_prices=False, date="2025-03-03"):
    tarifs = 0
    if tariff == "G11":
        tarifs = G11_TAURON
    elif tariff == "G12":
        tarifs = G12_TAURON
    elif tariff == "G13":
        tarifs = G13_TAURON
    elif tariff == "G14":
        file_path = f"../data_months/kompas_energetyczny/{date}.csv"
        tarifs = np.array((pd.read_csv(file_path).values).flatten())
    else:
       print("wrong tarrif!!!!")

    if static_prices:
        prices = np.full(SIZE, TAURON_STATIC_KWH) + tarifs
        return prices, sell_prices, TAURON_MONTHLY_COST_STATIC
    netto_prices = prices + SC_TAUTRON
    brutto_prices = netto_prices * (1 + VAT)
    buy_prices = np.maximum(TAURON_MIN_PRICE_CAP,brutto_prices) + tarifs
    sell_prices = sell_prices * ADDITIONAL_HELPER_SELLING
    
    return buy_prices, sell_prices, TAURON_MONTHLY_COST