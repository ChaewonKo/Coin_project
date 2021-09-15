import sys, time, requests
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyupbit
import finplot as fplt

class Coin_trade_bot_GUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle('재정 거래 프로그램')

        layout = QVBoxLayout() # 전체 레이아웃

        self.row_1 = QHBoxLayout()
        self.row_2 = QHBoxLayout()

        ## 2 x 2 grid
        self.set_pos_1_1() # set Point(1, 1)
        self.row_1.addLayout(self.pos_1_1) # Point(1, 1)

        self.set_pos_1_2() # set Point(1, 2)
        self.row_1.addLayout(self.pos_1_2) # Point(1, 2)

        self.set_pos_2_1() # set Point(2, 1)
        self.row_2.addLayout(self.pos_2_1) # Point(2, 1)

        self.set_pos_2_2() # set Point(2, 2)
        self.row_2.addLayout(self.pos_2_2) # Point(2, 2)

        layout.addLayout(self.row_1)
        layout.addLayout(self.row_2)
        self.setLayout(layout)
        self.show()

    def set_pos_1_1(self):
        self.pos_1_1 = QVBoxLayout()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.pos_1_1.addWidget(self.canvas)

    def set_pos_1_2(self):
        self.pos_1_2 = QFormLayout()
        self.balance = QLabel('11,456,740원', self)
        self.pos_1_2.addRow('주문 가능', self.balance)

    def set_pos_2_1(self):
        self.pos_2_1 = QGridLayout()
        self.pos_2_1.resize(400, 300)


        ax = fplt.create_plot(init_zoom_periods=100)
        self.axs = [ax] # finplot requres this property

        df = pyupbit.get_ohlcv("KRW-BTC")
        df.rename(columns={'open': "Open", "high": "High", "low": "Low", "close":"Close"}, inplace=True)
        
        fplt.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']])
        fplt.show(qt_exec=False)
        self.pos_2_1.addWidget(ax.vb.win, 0, 0)

    def set_pos_2_2(self):
        self.pos_2_2 = QHBoxLayout()
        self.balance_ = QLabel('11,456,740원', self)
        self.pos_2_2.addWidget(self.balance_)


class Coin_trade_bot():
    def __init__(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CB_GUI = Coin_trade_bot_GUI()
    app.exec_()

''' 참고 자료
https://github.com/sharebook-kr/pyupbit/tree/master/example
https://github.com/matplotlib/mplfinance
https://github.com/highfestiva/finplot/tree/master/finplot/examples
https://wikidocs.net/31063
https://wikidocs.net/4766
https://wikidocs.net/135133
'''