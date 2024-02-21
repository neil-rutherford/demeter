import sqlite3
import datetime

def create_database(seed_funds=200):
    '''
    Generates tables for database. Use once.
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS advice(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        price REAL, 
        sma REAL, 
        standard_deviation REAL, 
        upper_band REAL, 
        lower_band REAL, 
        advice TEXT, 
        timestamp TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trade(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        amount REAL, 
        buy_advice_id INTEGER,
        buy_price REAL, 
        buy_timestamp TEXT, 
        sell_advice_id INTEGER,
        sell_price REAL, 
        sell_timestamp TEXT, 
        profit_multiplier REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS account(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        trade_id INTEGER,
        balance REAL, 
        timestamp TEXT
    )
    """)
    con.close()
    create_seed_funds(seed_funds)


def create_advice(price, sma, standard_deviation, upper_band, lower_band, advice):
    '''
    Creates an entry in the Advice table. Used to record calculations and buy/sell recommendations.

    :param price:               Price of BTC at a given point, as a float.
    :param sma:                 Simple Moving Average of historic price data, as a float.
    :param standard_deviation:  Standard deviation of historic price data, as a float.
    :param upper_band:          Upper Bollinger band for historic price data, as a float.
    :param lower_band:          Lower Bollinger band for historic price data, as a float.
    :param advice:              BUY / SELL / HOLD, as a string.
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO advice VALUES (?,?,?,?,?,?,?,?)", 
        (None, float(price), float(sma), float(standard_deviation), float(upper_band), float(lower_band), str(advice), str(timestamp))
    )
    con.commit()
    con.close()


def read_advices(limit):
    '''
    Retrieves x last entries from the Advice table. Used to make buy/sell decisions.

    :param limit:   How many entries do you want to retrieve, as an integer?
    :rtype:         List of dictionaries
    '''
    limit = int(limit)
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM advice ORDER BY id DESC LIMIT {int(limit)}")
    results = res.fetchall()
    data_list = []
    for x in results:
        data_dict = {
            'id': x[0],
            'price': x[1],
            'sma': x[2],
            'standard_deviation': x[3],
            'upper_band': x[4],
            'lower_band': x[5],
            'advice': x[6],
            'timestamp': x[7]
        }
        data_list.append(data_dict)
    return data_list


def create_buy(amount, buy_advice_id, buy_price):
    '''
    Creates a buy entry in the Trades table. Used to simulate buys.

    :param amount:          How much money did we spend on this buy, as a float?
    :param buy_advice_id:   What is the primary key of the Advice that prompted this buy, as an integer?
    :param buy_price:       What price did we buy BTC at, as a float?
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    buy_timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO trade VALUES (?,?,?,?,?,?,?,?,?)", 
        (None, float(amount), int(buy_advice_id), float(buy_price), str(buy_timestamp), None, None, None, None)
    )
    con.commit()
    con.close()


def read_trades(limit):
    '''
    Retrieves x last entries in the Trade table. Used to get both buy and sell data.

    :param limit:   How many entries do you want to retrieve, as an integer?
    :rtype:         List of dictionaries
    '''

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM trade ORDER BY id DESC LIMIT {int(limit)}")
    results = res.fetchall()
    data_list = []
    for x in results:
        data_dict = {
            'id': x[0],
            'amount': x[1],
            'buy_advice_id': x[2],
            'buy_price': x[3],
            'buy_timestamp': x[4],
            'sell_advice_id': x[5],
            'sell_price': x[6],
            'sell_timestamp': x[7],
            'profit_multiplier': x[8]
        }
        data_list.append(data_dict)
    return data_list


def create_sell(trade_id, sell_advice_id, sell_price, profit_multiplier):
    '''
    Creates a sell entry in the Trades table. Used to update buy entries and simulate trades.

    :param trade_id:            What is the primary key of the Trade this is linked to, as an integer? (You need to buy before you can sell.)
    :param sell_advice_id:      What is the primary key of the Advice that prompted this sell, as an integer?
    :param sell_price:          How much did we sell at, as a float?
    :param profit_multiplier:   (Sell price) / (Buy price), as a float.
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    sell_timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "UPDATE trade SET sell_advice_id = ?, sell_price = ?, sell_timestamp = ?, profit_multiplier = ? WHERE id = ?",
        (int(sell_advice_id), float(sell_price), str(sell_timestamp), float(profit_multiplier), int(trade_id))
    )
    con.commit()


def create_seed_funds(amount):
    '''
    Creates the first entry in the Account table. Used to simulate the initial deposit of money.

    :param amount:  Amount of seed money, as a float.
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO account VALUES (?,?,?,?)", 
        (None, None, float(amount), str(timestamp))
    )
    con.commit()
    con.close()


def update_funds(trade_id, amount):
    '''
    Creates a new entry in the Account table as trades are made. Used to simulate money flow with buys and sells.

    :param trade_id:    What is the primary key of the trade that is affecting the balance, as an integer?
    :param amount:      What is the new amount of money in the account, as a float? 
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO account VALUES (?,?,?,?)", 
        (None, int(trade_id), float(amount), str(timestamp))
    )
    con.commit()
    con.close()


def read_account_balances(limit):
    '''
    Returns the last n account balances, in reverse chronological order (newest is first). Used to read historical account data.

    :param limit:   Number of entries to retrieve, as an integer
    :rtype:         List of floats
    '''
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM account ORDER BY id DESC LIMIT {int(limit)}")
    raw_data = res.fetchall()
    con.close()
    data_list = []
    for x in raw_data:
        data_dict = {
            'id': x[0],
            'trade_id': x[1],
            'balance': x[2],
            'timestamp': x[3]
        }
        data_list.append(data_dict)
    return data_list  


def purge_old_advices(older_than=365):
    '''
    Deletes advice entries that are over 1 year old. Used to prevent database from getting too big.

    :param older_than:      Delete older than x days, as an integer
    :rtype:                 None
    '''
    now = datetime.datetime.now(datetime.UTC)
    limit = now - datetime.timedelta(days=int(older_than))
    condition = limit.strftime('%Y-%m-%d %H:%M')

    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute(
        f'DELETE FROM advice WHERE timestamp LIKE "{condition}:%"'
    )
    con.commit()
    con.close()
