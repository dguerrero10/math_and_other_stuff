import requests as req
import sys
import http.client
from json import loads

import numpy as np
from time import sleep

class ConnectionHandler:
    def __init__(self):
        try: 
            self.BASE_ENDPOINT = "coingecko.p.rapidapi.com"
            self.conn = http.client.HTTPSConnection(self.BASE_ENDPOINT)
            self.headers = {
                            'x-rapidapi-host': "coingecko.p.rapidapi.com",
                            'x-rapidapi-key': "b3fea2a343msh4d3a7ed26494714p1459c5jsnaa3919fd6504"
                            }
        except:
            sys.exit(f'Could not establish connection with {self.BASE_ENDPOINT}\n')

class PriceFetcher():
    def __init__(self, route):
        self.conn_handler = ConnectionHandler()
        self.route = route

        self.coin_strings = '''auction,bitcoin,ethereum,
        solana,cardano,polkadot,dogecoin,shiba-inu,uniswap,chainlink,litecoin,algorand,
        bitcoin-cash,axie-infinity,cosmos,internet-computer,filecoin,
        ethereum-classic,dai,tezos,the-graph,decentraland,aave,eos,
        maker,terrausd,chiliz,celo,zcash,dash,curve-dao-token,
        loopring,basic-attention-token,iotex,perpetual-protocol,
        ankr,paxos-standard,skale,1inch,livepeer,uma,
        origintrail,nucypher,storj,polymath,coti,numeraire,cartesi,
        badger-dao,nkn,band-protocol,civic,augur,rally,braintrust,keep-network,tribe,
        playdapp,mask-network,truefi,alchemy-pay,lcx,mirror-protocol,orion-protocol,
        radicle,arpa-chain,adventure-gold,balancer,clover-finance'''

        self.coin_strings = ''.join(self.coin_strings.split())
        self.coin_list = self.coin_strings.split(',')
        self.p1_vect = []
        self.p2_vect = []
        self.diff_vect = []

    def addDataToVects(self, vector, data_JSON):
        for i in range(len(self.coin_list)):
            for name, price in data_JSON.items():
                if self.coin_list[i] == name:
                    if vector == 'p1':
                        self.p1_vect.append(price['usd'])
                        self.p2_vect.append(0)
                    else:
                        self.p2_vect[i] = price['usd']
        return

    def getInitialPrices(self):
        # Get prices and store in list[dict] format
        self.conn_handler.conn.request("GET", f"{self.route}?ids={self.coin_strings}&vs_currencies=usd", headers=self.conn_handler.headers)

        response = self.conn_handler.conn.getresponse()
        data = response.read()
        data_JSON = loads(data.decode('utf-8'))

        self.addDataToVects('p1', data_JSON)
        return

    def getCurrentPrices(self):
        # Get prices and store in array
        self.conn_handler.conn.request("GET", f"{self.route}?ids={self.coin_strings}&vs_currencies=usd", headers=self.conn_handler.headers)

        response = self.conn_handler.conn.getresponse()
        data = response.read()
        data_JSON = loads(data.decode('utf-8'))

        self.addDataToVects('p2', data_JSON)
        return

    def comparePriceChange(self):
        self.getCurrentPrices()

        v_1 = np.array(self.p1_vect)
        v_2 = np.array(self.p2_vect)

        diff = v_2 - v_1

        self.diff_vect = np.divide(diff, v_1)

        print(self.diff_vect)
 
        target_coins = ''

        for i in range(len(self.diff_vect)):
            if self.diff_vect[i] < 0:
                target_coins += self.coin_list[i] + ','

        if len(target_coins) == 0:
            return None
        else:
            return target_coins


class PriceChangeAnalysis():
    def __init__(self, target_coins):
       self.conn_handler = ConnectionHandler()
       self.target_coins = target_coins
       self.coin_price_movements = []
  
    def getMarketData(self):
        self.conn_handler.conn.request("GET", f"/coins/markets?vs_currency=usd&page=1&per_page=100&ids={self.target_coins}&order=market_cap_desc", headers=self.conn_handler.headers)

        response = self.conn_handler.conn.getresponse()
        data = response.read()
        data = data.decode('utf-8')

        # print(data)
    
    def getMarketChartData(self):
        for coin in self.target_coins.split(','):
            self.conn_handler.conn.request("GET", f"/coins/{coin}/market_chart?vs_currency=usd&days=20", headers=self.conn_handler.headers)

            response = self.conn_handler.conn.getresponse()
            data = response.read()
            data_JSON = loads(data.decode('utf-8'))

            price_movements = []

            try:
                for price in data_JSON['prices']:
                    price_movements.append(price[-1])

                d = {coin: price_movements}
                self.coin_price_movements.append(d)
                
            except:
                continue

        print(self.coin_price_movements)
        
PF = PriceFetcher('/simple/price')
PF.getInitialPrices()

def run():
    while True:
        sleep(20)
        target_coins = PF.comparePriceChange()
        if target_coins == None:
            return run()
        else:
            PCA = PriceChangeAnalysis(target_coins)
            # PCA.getMarketData()
            PCA.getMarketChartData()
run()