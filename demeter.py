import funcs
import schedule
import time

def main(days=20, desired_profit=1.00):
    try:
        funcs.purge()

        # Save BTC price
        price = funcs.get_btc_price()

        # Load data 
        data = funcs.load_price_data(days=days)

        # Use data to generate advice
        advice = funcs.make_advice(
            price=price,
            data=data
        )

        if advice['advice'] == "BUY":
            funcs.buy(advice)
        
        elif advice['advice'] == 'SELL':
            funcs.sell(advice, desired_profit)

        else:
            pass
    
    except:
        pass

schedule.every().minute.at(":15").do(main)
schedule.every().minute.at(":45").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
