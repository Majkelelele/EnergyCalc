from backend.const import CURRENT_A, B_ENEA, VAT, ENEA_MONTHLY_COST, ENERGA_MONTHLY_COST, PGE_MONTHLY_COST, TAURON_MONTHLY_COST, K_PGE, SC_TAUTRON, Wk_ENERGA, ENEA_STATIC_KWH, PGE_STATIC_KWH, TAURON_STATIC_KWH, ENERGA_STATIC_KWH, ENEA_MONTHLY_COST_STATIC, ENERGA_MONTHLY_COST_STATIC, TAURON_MONTHLY_COST_STATIC, PGE_MONTHLY_COST_STATIC, SIZE, PGE_MIN_PRICE_CAP, TAURON_MIN_PRICE_CAP, G13_TAURON, G11_TAURON, G12_TAURON
import numpy as np

def calculate_enea_price(prices, static_prices=False):
    if static_prices:
        prices = np.full(SIZE, ENEA_STATIC_KWH)
        return prices, ENEA_MONTHLY_COST_STATIC
    netto_prices = prices + CURRENT_A + B_ENEA
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, ENEA_MONTHLY_COST


def calculate_energa_prices(prices, static_prices=False):
    if static_prices:
        prices = np.full(SIZE, ENERGA_STATIC_KWH)
        return prices, ENERGA_MONTHLY_COST_STATIC
    netto_prices = prices + Wk_ENERGA
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, ENERGA_MONTHLY_COST


def calculate_pge_prices(prices, static_prices=False):
    if static_prices:
        prices = np.full(SIZE, PGE_STATIC_KWH)
        return prices, PGE_MONTHLY_COST_STATIC
    prices = np.maximum(PGE_MIN_PRICE_CAP, prices)
    netto_prices = prices + CURRENT_A + K_PGE
    brutto_prices = netto_prices * (1 + VAT)
    return  brutto_prices, PGE_MONTHLY_COST

def calculate_tauron_prices(prices, tariff = "G11", static_prices=False):
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
        prices = np.full(SIZE, TAURON_STATIC_KWH) + tarifs
        return prices, prices, TAURON_MONTHLY_COST_STATIC
    netto_prices = prices + SC_TAUTRON
    brutto_prices = netto_prices * (1 + VAT)
   
    buy_prices = np.maximum(TAURON_MIN_PRICE_CAP,brutto_prices) + tarifs
    sell_prices = 0.9 * buy_prices
    return buy_prices, sell_prices, TAURON_MONTHLY_COST