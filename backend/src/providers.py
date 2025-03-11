from backend.const import CURRENT_A, B_ENEA, VAT, ENEA_MONTHLY_COST, ENERGA_MONTHLY_COST, PGE_MONTHLY_COST, TAURON_MONTHLY_COST, K_PGE, SC_TAUTRON, Wk_ENERGA


def calculate_enea_price(prices):
    netto_prices = prices + CURRENT_A + B_ENEA
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, ENEA_MONTHLY_COST


def calculate_energa_prices(prices):
    netto_prices = prices + Wk_ENERGA
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, ENERGA_MONTHLY_COST


def calculate_pge_prices(prices):
    netto_prices = prices + CURRENT_A + K_PGE
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, PGE_MONTHLY_COST

def calculate_tauron_prices(prices):
    netto_prices = prices + SC_TAUTRON
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, TAURON_MONTHLY_COST