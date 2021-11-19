import os
import matplotlib.pyplot as plt
import requests as req
import numpy as np
import time
from datetime import datetime

class PriceFetcher():
    # Intialize api endpoint and parameters
    def __init__(self):
        self.endpoint = 'https://coingecko.p.rapidapi.com/simple/price'
        self.s_coins = '''litecoin,aave,dogecoin,algorand,ankr,balancer,augur,band-protocol,bitcoin,bitcoin-cash,cardano,celo,cartesi,chainlink,civic,dash,dai,ethereum,ethereum-classic'''
        self.coins = self.s_coins.split(',')
        self.querystring = {"ids":self.s_coins, "vs_currencies":"usd"}
        self.headers = {
                        'x-rapidapi-key': "b3fea2a343msh4d3a7ed26494714p1459c5jsnaa3919fd6504",
                        'x-rapidapi-host': "coingecko.p.rapidapi.com"
                       }

    def getPrices(self):
        # Get prices and store in list[dict] format
        response = req.get(self.endpoint, params=self.querystring, headers=self.headers).json()
        price_coin_pairs = []

        for i in range(len(self.coins)):
            price = response[self.coins[i]]['usd']
            d = {self.coins[i]: price}
            price_coin_pairs.append(d)

        return price_coin_pairs

class MarketObserver():
    def __init__(self, price_coin_pairs):
        self.price_coin_pairs = price_coin_pairs
        self.price_obsv = PriceFetcher()

    def priceDifference(self):
        time.sleep(10)

        # Fetch latest market data
        price_coin_pairs_change = self.price_obsv.getPrices()

        # Unpack dictionaries and store prices in list[]
        vector_1 = []
        vector_2 = []

        for coin in self.price_coin_pairs:
            for price in coin.values():
                vector_1.append(price)        
        for coin in price_coin_pairs_change:
            for price in coin.values():
                vector_2.append(price)

        # Convert lists to numpy arrays for easier calculations
        vector_1 = np.array(vector_1)
        vector_2 = np.array(vector_2)

        # Calculate price difference 
        price_diff = vector_2 - vector_1
        price_diff_percent = np.divide(price_diff, vector_1) * 100

        # Track potential market movers
        coins_to_analyze = []

        for i in range(len(self.price_coin_pairs)):
            if price_diff_percent[i] > 0 or price_diff_percent[i] < 0 or price_diff_percent[i] == 0:
                coin = self.price_coin_pairs[i]
                price = price_diff_percent[i]
                for name in coin.keys():
                    coins_to_analyze.append({name: price})

        # Run function recursively until until len(price_coin_analysis) > 0
        if len(coins_to_analyze) == 0:
            self.priceDifference()
        else:
            return coins_to_analyze

class HistoricalDataAnalyzer():
    def __init__(self, coins_to_analyze):
        # Iterate through coins to analyze and interpolate into endpoint string
        self.endpoints = []
        self.coins_to_analyze = coins_to_analyze
        for coin in self.coins_to_analyze:
            for name in coin.keys():
                self.endpoints.append(f'https://coingecko.p.rapidapi.com/coins/{name}/market_chart/range')
        # Get the last 18 minutes of market data for each coin by getting current UNIX timestamp and substracting 600 seconds 
        from_timestamp = time.time() - 1000
        from_timestamp = str(from_timestamp)
        to_timestamp = time.time()
        to_timestamp = str(to_timestamp)
        # Add timestamps to querystring
        self.querystring = {"from":from_timestamp,"vs_currency":"usd","to":to_timestamp}
        # Get headers from PriceFetcher class
        headers = PriceFetcher()
        self.headers = headers.headers

    def timeChangeHelper(self, t1, t2):
        # Divide timestamps by 100 to avoid "year out of range error"
        t1 = t1 / 100
        t2 = t2 / 100
        # Convert unix time to military time
        d1 = datetime.utcfromtimestamp(t1).strftime('%H:%M:%S')
        d2 = datetime.utcfromtimestamp(t2).strftime('%H:%M:%S')
        # Convert string to datetime object for calculating difference 
        d1 = datetime.strptime(d1, '%H:%M:%S')
        d2 = datetime.strptime(d2, '%H:%M:%S')

        # Subtract later time from earlier time
        diff = d2 - d1
        # Get seconds from object to convert to minutes
        seconds = diff.total_seconds()
        # Get minutes by dividing seconds by 60
        minutes = int(seconds / 60) % 60

        return minutes

    def getHistoricalData(self):
        # Make requests and store data
        responses = []

        for endpoint in self.endpoints:
            response = req.get(endpoint, params=self.querystring, headers=self.headers).json()
            responses.append(response)

        # Store coin names 
        coin_names = []

        for coin in self.coins_to_analyze:
            for name in coin.keys():
                coin_names.append(name)

        # Unpack response data by grabbing price and timestamp lists 
        # Store data in a dictionary with the 'key' being the coin name
        # Append dictionary to one list
        coin_historical_data = []

        j = 0
        for res in responses:
            d = {coin_names[j]: res['prices']}
            coin_historical_data.append(d)
            j += 1

        self.computeChange(coin_historical_data)

    def computeChange(self, coin_historical_data):
        price_changes = []
        time_changes = []

        for i in range(len(coin_historical_data)):
            coin = coin_historical_data[i]
            for name, value in coin.items():
                for coin in range(len(value) -1):
                    price_change = value[coin+1][1] - value[coin][1]
                    price_change = (price_change / value[coin][1]) * 100
                    time_change = self.timeChangeHelper(value[coin][0], value[coin+1][-1])
                    price_changes.append(price_change)
                    time_changes.append(time_change)
                
                coin_changes_summary = {name:[time_changes, price_changes]}
                self.analyzeHistoricalData(coin_changes_summary)
                price_changes.clear()
                time_changes.clear()
        
    def analyzeHistoricalData(self, coin_changes_summary):
        for name, value in coin_changes_summary.items():
            print(value)
            v_range = value[0][0] - value[0][-1]
            print(v_range)
            x = plt.xlim(0, v_range)
            y = value[1]
            
            plt.plot(x, y)
            plt.title(name)
            plt.xlabel('Minutes')
            plt.ylabel('Rate of change (Price)')
            plt.show()


if __name__ == '__main__':
    # Get initial market prices
    price_fetcher = PriceFetcher()
    price_coin_pairs = price_fetcher.getPrices()
    # Watch for potential market movements
    market_observer = MarketObserver(price_coin_pairs)
    coins_to_analyze = market_observer.priceDifference()
    # Wait 5 minutes and to give market time to continue moving
    time.sleep(30)
    # Analyze market data of last 10 minutes to detect upward movement
    historical_data_analyzer = HistoricalDataAnalyzer(coins_to_analyze)
    historical_data_analyzer.getHistoricalData()