import json
import os


async def user_amount_conversion(currency, city, amount):
    filepath = f"./best_rate/best_rate.json"
    currency = currency.replace(" -> ", "_")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if currency == "USD_PL" or currency == "EUR_PL":
        return round(amount * data[city][currency], 2), data[city][currency]
    
    elif currency == "PL_USD" or currency == "PL_EUR":
        return round(amount / data[city][currency], 2), data[city][currency]
