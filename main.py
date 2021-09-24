import sys, time, pybithumb, pyupbit
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QProgressBar, QApplication, QMainWindow, QBoxLayout, QLabel, QListWidgetItem
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal, QPropertyAnimation
form_class = uic.loadUiType("resources/main.ui")[0]

class PriceWorker(QThread):
    priceDataSent = pyqtSignal(float)

    def __init__(self, ticker_name):
        super().__init__()
        self.ticker_name = ticker_name # KRW-BTC
        self.alive = True

    def run(self):
        while self.alive:
            # data  = pybithumb.get_current_price(self.ticker) # for bithumb
            data = pyupbit.get_current_price(self.ticker_name)
            time.sleep(0.2)
            if data != None:
                self.priceDataSent.emit(data)
            else :
                self.priceDataSent.emit(-1.0)

    def change_ticker(self, ticker_name):
        self.alive = False
        self.ticker_name = ticker_name
        self.alive = True

    def close(self):
        self.alive = False
        self.quit()
        self.wait(5000)

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

    def change_ticker(self, ticker_name):
        self.alive = False
        self.ticker_name = ticker_name
        self.alive = True

    def close(self):
        self.alive = False
        self.quit()
        self.wait(5000)

class Item(QWidget):
    def __init__(self, ticker, list_type):
        QWidget.__init__(self, flags=Qt.Widget)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.ticker = ticker
        layout.addWidget(QLabel(self.ticker[list_type]))
        layout.addWidget(QLabel(self.ticker['market']))
        # layout.setSizeConstraint(QBoxLayout.SetFixedSize)
        self.setLayout(layout)

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = 'KRW-BTC'
        # self.upbit = pyupbit()
        self.tickers_list_widget()
        self.chart_widget()
        self.orderbook_widget()
        
        self.pushButton.clicked.connect(self.inDetailBtn)

        self.setWindowTitle("Home Trading System")

    def tickers_list_widget(self, lang='korean_name', price_type='KRW'):
        ''' 
        list_type : (default)korean_name, marker, english_name
        price_type : (default)KRW, BTC, USDT
        '''
        for ticker in pyupbit.get_tickers(price_type):
            self.add_tickers_list_widget(
                ticker=ticker,
                list_type=lang,
                price_type=price_type
            )

        self.tickerList.itemClicked.connect(self.change_chart)

    def add_tickers_list_widget(self, ticker, list_type, price_type):
            item = QListWidgetItem(self.tickerList)
            custom_widget = Item(ticker=ticker, list_type=list_type)
            item.setSizeHint(custom_widget.sizeHint())
            item.setWhatsThis(ticker['market'])
            self.tickerList.setItemWidget(item, custom_widget)
            self.tickerList.addItem(item)


    def change_chart(self, ticker):
        print('현재 선택된 항목 :', self.tickerList.currentItem().whatsThis())
        print('ow is running? :', self.ow.isRunning())
        print('pw is running? :', self.pw.isRunning())
        if self.ow.isRunning():
            self.ow.terminate()
            self.ow.wait()
            self.ow.start()
        
        if self.pw.isRunning():
            self.pw.terminate()
            self.pw.wait()
            self.pw.start()


    def orderbook_widget(self, ticker='KRW-BTC'): # for orderbook
        for i in range(self.tableBids.rowCount()):
            # 매도호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 0, item_0)

            item_1 = QProgressBar(self.tableAsks)
            item_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_1.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0);border : 0;font: 8px;height: 5px;}
                QProgressBar::Chunk {background-color : rgba(255, 0, 0, 0.5);border : 0;width: 5px}
            """)
            self.tableAsks.setCellWidget(i, 1, item_1)

            # 매수호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableBids.setItem(i, 0, item_0)

            item_1 = QProgressBar(self.tableBids)
            item_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_1.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0);border : 1;font: 8px;height: 5px;}
                QProgressBar::Chunk {background-color : rgba(0, 255, 0, 0.4);border : 1;width: 5px}
            """)
            self.tableBids.setCellWidget(i, 1, item_1)
        self.ow = OrderbookWorker(ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

    def updateData(self, data): # for orderbook
        if data == dict():
            return
        max_size = 0

        N = self.tableBids.rowCount()
        for size in data['orderbook_units'][:N]:
            max_size = max(size['ask_size'], size['bid_size'], max_size)
        max_size = int(max_size * 100)
        for i, v in enumerate(data['orderbook_units'][:N]):
            # 매도호가
            item_0 = self.tableAsks.item(N-1-i, 0)
            item_0.setText(f"{v['ask_price']:,}")
            item_1 = self.tableAsks.cellWidget(N-1-i, 1)
            item_1.setRange(0, max_size)
            item_1.setFormat(f"{v['ask_size']:,}")
            item_1.setValue(int(v['ask_size']*100))

            # 매수호가
            item_0 = self.tableBids.item(i, 0)
            item_0.setText(f"{v['bid_price']:,}")
            item_1 = self.tableBids.cellWidget(i, 1)
            item_1.setRange(0, max_size)
            item_1.setFormat(f"{v['bid_size']:,}")
            item_1.setValue(int(v['bid_size']*100))

    def chart_widget(self, ticker='KRW-BTC'): # for chart
        self.ticker = ticker
        self.viewLimit = 128

        self.priceData = QLineSeries()
        self.priceChart = QChart()
        self.priceChart.addSeries(self.priceData)
        self.priceChart.legend().hide()

        axisX = QDateTimeAxis()
        axisX.setFormat("hh:mm:ss")
        axisX.setTickCount(4)
        dt = QDateTime.currentDateTime()
        axisX.setRange(dt, dt.addSecs(self.viewLimit))
        axisY = QValueAxis()
        axisY.setVisible(False)

        self.priceChart.addAxis(axisX, Qt.AlignBottom)
        self.priceChart.addAxis(axisY, Qt.AlignRight)
        self.priceData.attachAxis(axisX)
        self.priceData.attachAxis(axisY)
        self.priceChart.layout().setContentsMargins(0, 0, 0, 0)

        self.priceView.setChart(self.priceChart)
        self.priceView.setRenderHints(QPainter.Antialiasing)

        self.pw = PriceWorker(ticker)
        self.pw.priceDataSent.connect(self.appendData)
        self.pw.start()

    def appendData(self, currPirce): # for chart
        if currPirce == -1.0:
            return
        
        if len(self.priceData) == self.viewLimit :
            self.priceData.remove(0)
        dt = QDateTime.currentDateTime()
        self.priceData.append(dt.toMSecsSinceEpoch(), currPirce)
        self.__updateAxis()

    def __updateAxis(self): # for chart
        pvs = self.priceData.pointsVector()
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.priceData) == self.viewLimit :
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)
        ax = self.priceChart.axisX()
        ax.setRange(dtStart, dtLast)

        ay = self.priceChart.axisY()
        dataY = [v.y() for v in pvs]
        ay.setRange(min(dataY), max(dataY))

    def inDetailBtn(self): # 자세히 보기 버튼
        print('자세히 보기 버튼 클릭!')
    

if __name__== '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())