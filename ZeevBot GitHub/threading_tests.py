import threading
import time
import logging
import json
import urllib.request

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

class ThreadPool(object):
    def __init__(self):
        super(ThreadPool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            # logging.debug('Running: %s', self.active)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            # logging.debug('Thread %s ended', name)


def bP(t, s, pool):
    #logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        try:
            token_eth = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=ETH-" + t))
            token_btc = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=BTC-" + t))
            usd_btc = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=usdt-btc"))
            usd_eth = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=usdt-eth"))
        except urllib.error.URLError:
            print("timeout")
            pool.makeInactive(name)
            return
        try:
            token_usd_eth = usd_eth['result']['Ask'] * token_eth['result']['Bid']
        except TypeError:
            token_usd_eth = 0
            # print("No arb")
            pool.makeInactive(name)
            return
        try:
            token_usd_btc = usd_btc['result']['Ask'] * token_btc['result']['Bid']
        except TypeError:
            token_usd_btc = 0
            # print("No arb")
            pool.makeInactive(name)
            return
        if (token_usd_btc > token_usd_eth):
            profit = (token_usd_btc - token_usd_eth)
        elif (token_usd_btc < token_usd_eth):
            profit = (token_usd_eth - token_usd_btc)
        elif (token_usd_btc == token_usd_eth):
            profit = 0
        tx_fee = (profit / 100) / 4
        if (profit > .2 and token_usd_eth != 0 and token_usd_btc != 0):
            print(t + " If you buy in terms of BTC, this token will cost $" + str(token_usd_btc) + " In terms of ETH it will cost: $" + str(token_usd_eth) +  " USD profit per " + t + " : $" + str(profit - tx_fee) + " Transaction fee: $" + str(tx_fee))
            pool.makeInactive(name)
            return
        else:
            #print("No arb here")
            pool.makeInactive(name)
            return

if __name__ == '__main__':
    pool = ThreadPool()
    s = threading.Semaphore(10)
    threads = []
    tokens = {'SALT'};
    marketSnapshot = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getmarkets"))
    for r in marketSnapshot['result']:
        pivot = r['MarketCurrency']
        base = r['BaseCurrency']
        # market_string = base + "-" + pivot
        tokens.add(pivot)
    while 1:
        print("Starting batch...")
        threads = []
        count = 0
        start_time = time.time()
        for t in tokens:
            temp = threading.Thread(target=bP, name='thread_'+t, args=(t, s, pool))
            temp.start()
            threads.append(temp)
        for x in threads:
            count = count + 1
            x.join()
            # print(threading.active_count())
        end_time = time.time()
        total = end_time - start_time
        print("This batch took " + str(total) + " seconds to run " + str(count) +" threads. Waiting 30s for next batch...")
        # print("Sleeping 30 sec for next batch.")
        time.sleep(30)
    # for i in range(10):
    #     t = threading.Thread(target=f, name='thread_'+str(i), args=(s, pool))
    #     t.start()

