from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyupbit
import finplot as fplt
import coin_trade_bot as CT

class Coin_trade_bot_GUI(QWidget):
    def __init__(self, parent=None):
        print('coin_trade 시작!')
        super().__init__(parent)
        uic.loadUi
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
        self.pos_1_2 = QVBoxLayout()

        self.AI_trading_state = QFormLayout()

        # 1_2 1줄
        self.balance1 = QLabel('0원', self)
        self.AI_trading_state.addRow('주문 가능', self.balance1)

        # 1_2 2줄
        self.ratio_of_trade = QHBoxLayout()

        self.ratio_of_trade_value = QLineEdit(self)
        self.ratio_of_trade_ComboBox = QComboBox(self)

        self.ratio_of_trade.addWidget(self.ratio_of_trade_value)
        self.ratio_of_trade.addWidget(QLabel('%'))
        self.ratio_of_trade.addWidget(self.ratio_of_trade_ComboBox)
        
        self.AI_trading_state.addRow('자동 거래 비율', self.ratio_of_trade)

        # 1_2 3줄
        self.price_of_trade = QHBoxLayout()
        self.price_of_trade_value = QLineEdit(self)

        self.price_of_trade.addWidget(self.price_of_trade_value)
        self.price_of_trade.addWidget(QLabel('원'))

        self.AI_trading_state.addRow('자동 거래 금액', self.price_of_trade)

        # 1_2 4줄
        self.investment_propensity = QHBoxLayout()

        self.investment_propensity_short = QCheckBox('단기', self)
        self.investment_propensity_long = QCheckBox('장기', self)

        self.investment_propensity.addWidget(self.investment_propensity_short)
        self.investment_propensity.addWidget(self.investment_propensity_long)

        self.AI_trading_state.addRow('투자 성향', self.investment_propensity)
        self.pos_1_2.addLayout(self.AI_trading_state)

        # 1_2 5줄
        self.btn_in_detail = QPushButton('자세히 보기', self)
        self.pos_1_2.addWidget(self.btn_in_detail)

        # 1_2 6줄
        hbox = QHBoxLayout()
        self.AI_start = QPushButton('자동 거래 시작', self)
        self.AI_stop = QPushButton('자동 거래 중지', self)

        hbox.addWidget(self.AI_start)
        hbox.addWidget(self.AI_stop)

        self.pos_1_2.addLayout(hbox)

    def set_pos_2_1(self):
        self.pos_2_1 = QGridLayout()
        # self.pos_2_1.setStyleSheet('border-width: 2px; border-color: #FA8072;')

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