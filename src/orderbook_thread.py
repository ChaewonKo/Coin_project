import time
from PyQt5.QtCore import QThread, pyqtSignal
import pyupbit

class OrderbookWorker(QThread):
    dataSent = pyqtSignal(dict)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            # data  = pybithumb.get_orderbook(self.ticker, limit=10)
            data  = pyupbit.get_orderbook(tickers=self.ticker)
            time.sleep(0.5)
            
            if data != None and type(data) == list:
                self.dataSent.emit(data[0])
            else:
                self.dataSent.emit(dict())

    def change_ticker(self, ticker):
        self.alive = False
        self.ticker = ticker
        self.alive = True

    def close(self):
        self.alive = False
        self.quit()
        self.wait(5000)