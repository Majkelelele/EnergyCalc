from backend.const import CURRENT_A, B_ENEA, VAT, ENEA_MONTHLY_COST, ENERGA_MONTHLY_COST, PGE_MONTHLY_COST, TAURON_MONTHLY_COST, K_PGE, SC_TAUTRON, Wk_ENERGA, ENEA_STATIC_KWH, PGE_STATIC_KWH, TAURON_STATIC_KWH, ENERGA_STATIC_KWH, ENEA_MONTHLY_COST_STATIC, ENERGA_MONTHLY_COST_STATIC, TAURON_MONTHLY_COST_STATIC, PGE_MONTHLY_COST_STATIC, SIZE
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
    netto_prices = prices + CURRENT_A + K_PGE
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, PGE_MONTHLY_COST

def calculate_tauron_prices(prices, static_prices=False):
    if static_prices:
        prices = np.full(SIZE, TAURON_STATIC_KWH)
        return prices, TAURON_MONTHLY_COST_STATIC
    netto_prices = prices + SC_TAUTRON
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, TAURON_MONTHLY_COST