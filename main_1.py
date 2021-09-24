import sys
from PyQt5.QtWidgets import QApplication
import coin_trade_bot_GUI as CT_GUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CB_GUI = CT_GUI.Coin_trade_bot_GUI()
    app.exec_()

''' 참고 자료
https://github.com/sharebook-kr/pyupbit/tree/master/example
https://github.com/matplotlib/mplfinance
https://github.com/highfestiva/finplot/tree/master/finplot/examples
https://wikidocs.net/31063
https://wikidocs.net/4766
https://wikidocs.net/135133
'''