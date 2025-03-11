from backend.const import SIZE, CURRENT_A, CURRENT_B, VAT, ENEA_MONTHLY_COST


def calculate_enea_price(prices):
    netto_prices = prices + CURRENT_A + CURRENT_B
    brutto_prices = netto_prices * (1 + VAT)
    return brutto_prices, ENEA_MONTHLY_COST
