import time
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import pyupbit


class PriceWorker(QThread):
    priceDataSent = pyqtSignal(pd.DataFrame)
    # priceDataSent = pyqtSignal(float)

    def __init__(self, ticker_name):
        super().__init__()
        self.ticker_name = ticker_name # KRW-BTC
        self.alive = True
        self.interval = 0.1

    def run(self):
        while self.alive:
            # data  = pybithumb.get_current_price(self.ticker) # for bithumb

            data = pyupbit.get_ohlcv(self.ticker_name, interval="minute1", count=100)
            # print(data['open'][0])
            # print(len(data))

            # data = pyupbit.get_current_price(self.ticker_name)
            time.sleep(self.interval)
            
            if len(data):
                self.priceDataSent.emit(data)
            else:
                self.priceDataSent.emit(0)

    def change_ticker(self, ticker_name):
        self.alive = False
        self.ticker_name = ticker_name
        self.alive = True

    def close(self):
        self.alive = False
        self.quit()
        self.wait(5000)