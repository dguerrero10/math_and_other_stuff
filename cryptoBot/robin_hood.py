import os
import atexit
import requests as req
import time
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import strftime
import datetime
import pandas as pd
import numpy as np
import robin_stocks.robinhood as rh
from colorama import Fore, Back, Style
from colorama import init
init()

class SendEmail():
    def __init__(self):
        self.port = 465
        self.context = ssl.create_default_context()
        self.sender_email = 'cryptonotifier6969@gmail.com'
        self.sender_password = os.environ.get('crypto_bot_pass')
        self.receiver_email = 'daveabdouguerrero@gmail.com'
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = "CryptoBot Purchase"
        self.message["From"] = self.sender_email
        self.message["To"] = self.receiver_email

    def send_purchase_email(self, purchase_data):  
        text = f"""\
        Hi, Dave.
        At {purchase_data[1]} Crypto Bot purchased Ethereum for the price of: {purchase_data[1]}
        Currently monitoring price movements to sell position.
        This is an automated email sent using python.
        """
        html = f"""\
        <html>
        <body>
            <p>Hi, Dave.</p>
            <p>At {purchase_data[1]} Crypto Bot purchased Ethereum for the price of:<p/>
            <h3>{purchase_data[0]}</h3>
            <p>Currently monitoring price movements to sell position.</p>
            <p>This is an automated email sent using python.</p>
        </body>
        </html>"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        self.message.attach(part1)
        self.message.attach(part2)

        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, self.message.as_string())

    def send_sell_email(self, sell_data):  
        text = f"""\
        Hi, Dave.
        At {sell_data[1]} Crypto Bot sold Ethereum for the price of: {sell_data[1]}
        Currently monitoring price movements to buy new position.
        This is an automated email sent using python.
        """
        html = f"""\
        <html>
        <body>
            <p>Hi, Dave.</p>
            <p>At {sell_data[1]} Crypto Bot sold Ethereum for the price of:<p/>
            <h3>{sell_data[0]}</h3>
            <p>Currently monitoring price movements to buy new position.</p>
            <p>This is an automated email sent using python.</p>
        </body>
        </html>"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        self.message.attach(part1)
        self.message.attach(part2)

        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, self.message.as_string())

class DataFrameHelper():
    def __init__(self):
        self.purchase_date_col = []
        self.purchase_price_col = []
        self.sell_date_col = []
        self.sell_price_col = []
        self.profit_col = []
        self.profit_percent_col = []
        self.coin_type_col = []
        self.buy_price = 0
        self.sell_price = 0
        atexit.register(self.create_df_read_to_csv)

    def store_buy_data(self, buy_data):
        self.purchase_date_col.append(buy_data[1])
        self.buy_price = buy_data[0]
        self.purchase_price_col.append(self.buy_price)

    def store_sell_data(self, sell_data, coin):
        self.sell_date_col.append(sell_data[1])
        self.sell_price = sell_data[0]
        self.sell_price_col.append(self.sell_price)
        self.coin_type_col.append(coin)
        self.caculate_profit()

    def caculate_profit(self):
        profit = float(self.sell_price) - float(self.buy_price)
        profit_percentage = profit / self.buy_price
        self.profit_col.append(profit)
        self.profit_percent_col.append(profit_percentage)

    def create_df_read_to_csv(self):
        data_dict = {
            'coin': self.coin_type_col,
            'purchase_date': self.purchase_date_col,
            'purchase_price': self.purchase_price_col,
            'sell_date': self.sell_date_col,
            'sell_price': self.sell_price_col,
            'profit_in_dollars': self.profit_col,
            'profit_in_percentage': self.profit_percent_col
        }
        t = datetime.datetime.now().astimezone().strftime("%Y-%m-%d, %H:%M")
        df = pd.DataFrame.from_dict(data_dict)
        if len(df['purchase_price'] > 0):
            df.to_csv(f'./trade_data/profits_{t}.csv')

class CryptoBot():
    # Login to RobinHood account
    @staticmethod
    def login():
        try:
            robin_user = os.environ.get("robinhood_username")
            robin_pass = os.environ.get("robinhood_password")
            rh.login(username=robin_user, password=robin_pass, expiresIn=1000000)
            return (Fore.GREEN + 'Login successful!' + Style.RESET_ALL)
        except: 
            return (Fore.RED + 'ERROR: Unable to log in to your RobinHood account.' + Style.RESET_ALL)

    @staticmethod
    def logout():
        rh.logout()

    # Initialize class variables
    def __init__(self, coin, symbol):
        # 'coin' is the currecy being traded
        self.coin = coin
        # 'symbol' is the currencies' market symbol
        self.symbol = symbol
        # Endpoint of api to fetch coin price data
        self.endpoint = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={self.coin}'
        # Get account position on coin 
        self.account_position = rh.crypto.get_crypto_positions(info="quantity")
        # Get buying power of account
        self.buying_power = float(rh.build_user_profile()['equity'])
        # Set market price position as current market price
        res = req.get(self.endpoint).json()
        self.market_price_position = res[0]['current_price']
        self.df = DataFrameHelper()
        self.email = SendEmail()

    # Get string representation of class object
    def __str__(self):
         return str(self.__class__) + ": " + str(self.__dict__)

    # Update position on coin, i.e. how much of the coin is owned
    def update_position(self):
        self.account_position = rh.crypto.get_crypto_positions(info='quantity')

    # Update the market price the coin was bought at 
    def update_market_price_purchased_at(self, price_bought_at):
        self.market_price_position = price_bought_at

    # Get buying power 
    def get_buying_power(self):
         self.buying_power = float(rh.build_user_profile()['equity'])

    # Get current price of coin and unpack request to store price and timestamp
    def get_current_price(self):
        res = req.get(self.endpoint).json()
        coin_price = res[0]['current_price']
        timestamp = res[0]['ath_date']
        return (coin_price, timestamp)

    # Monitor the price of the coin and buy when price decreases by 3% 
    def monitor_price(self):
        base_price = self.get_current_price()
        print('\n------------------------------------------------\n')
        print(f'Monitoring price movements... {self.coin} price at {base_price[1]} is {base_price[0]}')
        print('\n------------------------------------------------\n')

        while True:
            time.sleep(300)
            current_price = self.get_current_price()
            price_var = current_price[0] - base_price[0]
            price_var_percentage = (price_var / base_price[0])
            print(f'Change in price: {price_var_percentage}')

            if (price_var_percentage <= -0.01 or  price_var_percentage >= 0.005):
                self.buy()
    
    # Calculate price difference between current price and current position  
    def calculate_price_diff(self):
        current_price = self.get_current_price()

        print('\n------------------------------------------------\n')
        print(f'Current position {self.market_price_position}') 
        print(f'{self.coin} price at {current_price[1]} is {current_price[0]}')
        print('\n------------------------------------------------\n')

        price_var = current_price[0] - self.market_price_position
        price_var_percentage = (price_var / self.market_price_position)

        print(f'Change in price: {price_var_percentage}')

        return price_var_percentage

    def determine_move(self):
        price_var_percentage = self.calculate_price_diff()
        if (price_var_percentage >= 0.01 or price_var_percentage <= -0.01):
            self.sell()
        else:
            self.determine_move()

    def buy(self):
        print(Fore.RED + 'Purchasing...' + Style.RESET_ALL)
        rh.orders.order_buy_crypto_by_price(self.symbol, self.buying_power, timeInForce='gtc')
        price_bought_at = self.get_current_price()
        purchase_data = [price_bought_at[0], datetime.datetime.now().astimezone().strftime("%Y-%m-%d, %H:%M")]
        self.update_market_price_purchased_at(purchase_data[0])
        # self.email.send_purchase_email(purchase_data)
        self.df.store_buy_data(purchase_data)
        self.determine_move()

    def sell(self):
        print(Fore.GREEN + 'Selling...' + Style.RESET_ALL)
        rh.orders.order_sell_crypto_by_price(self.symbol, self.buying_power, timeInForce='gtc')
        price_sold_at = self.get_current_price()
        sell_data = [price_sold_at[0], datetime.datetime.now().astimezone().strftime("%Y-%m-%d, %H:%M")]
        # self.email.send_sell_email(sell_data)
        self.df.store_sell_data(sell_data, self.coin)
        time.sleep(10)
        self.get_buying_power()
        self.monitor_price()

print(CryptoBot.login())
crypto_bot = CryptoBot('dogecoin', 'DOGE')
crypto_bot.monitor_price()

