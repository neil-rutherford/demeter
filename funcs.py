import requests
import json
import numpy
import db_utils

def get_btc_price():
    try:
        r = requests.get('https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT')
        return float(r.json()['price'])
    except:
        raise AssertionError("Problem getting price.")

def load_price_data(days):
    try:
        limit = int(days) * 2880
        r = requests.get(f'http://btcathena.pythonanywhere.com/r?limit={limit}')
        data = r.json()
        assert len(data) == limit
        return data
    except:
        raise AssertionError("Problem getting historical data.")

def make_advice(price, data):
    sma = sum(data) / len(data)
    standard_deviation = numpy.std(data)
    upper_band = sma + standard_deviation
    lower_band = sma - standard_deviation
    if float(price) <= float(lower_band):
        advice = "BUY"
    elif float(price) >= float(upper_band):
        advice = "SELL"
    else:
        advice = "HOLD"
    db_utils.create_advice(
        price=float(price),
        sma=float(sma),
        standard_deviation=float(standard_deviation),
        upper_band=float(upper_band),
        lower_band=float(lower_band),
        advice=str(advice)
    )
    return db_utils.read_advices(limit=1)[0]

def buy(buy_advice_dict):
    funds = db_utils.read_account_balances(limit=1)
    print(f"Funds: {funds}")

    if len(funds) == 0 or funds[0]['balance'] == 0.0:
        print("I'm not gonna buy anything!")
        pass
    else:
        last_trade = db_utils.read_trades(limit=1)
        if len(last_trade) == 1:
            if not last_trade[0]['sell_advice_id']:
                pass

        db_utils.create_buy(
            amount=funds[0]['balance'],
            buy_advice_id=buy_advice_dict['id'],
            buy_price=buy_advice_dict['price']
        )

        last_trade = db_utils.read_trades(limit=1)
        db_utils.update_funds(
            trade_id=last_trade[0]['id'],
            amount=0.0
        )
        return last_trade


def sell(sell_advice_dict, desired_profit):
    # If there are no entries in the transaction log, pass
    last_trade = db_utils.read_trades(limit=1)
    if len(last_trade) == 0 or last_trade[0]['sell_advice_id']:
        pass
    else:
        # If the proposed sale price is less than or equal to buy price, pass
        profit_multiplier = (float(sell_advice_dict['price']) / float(last_trade[0]['buy_price']))
        if profit_multiplier < float(desired_profit):
            pass
        else:
            # Update trade
            db_utils.create_sell(
                trade_id=last_trade[0]['id'],
                sell_advice_id=sell_advice_dict['id'],
                sell_price=sell_advice_dict['price'],
                profit_multiplier=profit_multiplier
            )
            # Update funds
            last_trade = db_utils.read_trades(limit=1)
            db_utils.update_funds(
                trade_id=last_trade[0]['id'],
                amount=((profit_multiplier) * (last_trade[0]['amount']))
            )
            return last_trade


def purge():
    db_utils.purge_old_advices()
