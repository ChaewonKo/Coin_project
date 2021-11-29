import sys, requests
import time
import pandas
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QApplication, QMainWindow, QBoxLayout, QLabel, QListWidgetItem
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtChart import QChart, QValueAxis, QDateTimeAxis, QCandlestickSeries, QCandlestickSet
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from pandas import Series
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.models import load_model
from konlpy.tag import Okt

from src.ai_thread import AiThread
from src.chart_thread import PriceWorker
from src.orderbook_thread import OrderbookWorker
# from src.ai_window import AiWindow

main_ui = uic.loadUiType("resources/main.ui")[0]

class Item(QWidget):
    def __init__(self, ticker, list_type):
        QWidget.__init__(self, flags=Qt.Widget)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.ticker = ticker
        layout.addWidget(QLabel(self.ticker[list_type]))
        layout.addWidget(QLabel(self.ticker['market']))
        self.setLayout(layout)

class MainWindow(QMainWindow, main_ui):
    ai_thread_command = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1680, 1020)
        self.ticker = 'KRW-BTC'
        # self.upbit = pyupbit()
        self.tickers_list_widget()
        self.chart_widget()
        self.orderbook_widget()
        self.article_init()
        
        self.pushButton_17.clicked.connect(self.inDetailBtn)

        self.setWindowTitle("Home Trading System")

    def tickers_list_widget(self, lang='korean_name', price_type='KRW'):
        ''' 
        list_type : (default)korean_name, marker, english_name
        price_type : (default)KRW, BTC, USDT
        '''
        url = "https://api.upbit.com/v1/market/all"
        tickers = requests.get(url=url).json()

        for ticker in tickers:
            if ticker['market'].startswith('KRW'):
                self.add_tickers_list_widget(
                    ticker=ticker,
                    list_type=lang,
                    price_type=price_type
                )

        self.tickerList.itemClicked.connect(self.change_chart)

    def add_tickers_list_widget(self, ticker, list_type, price_type):
            item = QListWidgetItem(self.tickerList)
            item.ticker = ticker
            custom_widget = Item(ticker=ticker, list_type=list_type)
            item.setSizeHint(custom_widget.sizeHint())
            item.setWhatsThis(ticker['market'])
            self.tickerList.setItemWidget(item, custom_widget)
            self.tickerList.addItem(item)

    def change_chart(self, ticker):
        self.ow.change_ticker(ticker=ticker.whatsThis())
        self.pw.change_ticker(ticker_name=ticker.whatsThis())

        self.label_15.setText(ticker.ticker['korean_name'])

    def orderbook_widget(self, ticker='KRW-BTC'): # for orderbook
        self.ow = OrderbookWorker(ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

    def updateData(self, data): # for orderbook
        if data == dict():
            return
        max_size = 0

        N = 4
        for size in data['orderbook_units'][:N]:
            max_size = max(size['ask_size'], size['bid_size'], max_size)
        max_size = int(max_size * 100)

        # print('v :', data)
        v = data['orderbook_units'][3]

        # row : 1
        # self.order_00.setText(f"{v['ask_price']:,}")
        self.order_01.setText(f"{v['ask_size']:,}")
        self.order_02.setText(f"{v['ask_price'] * v['ask_size']}")
        self.order_progress_0.setRange(0, max_size)
        self.order_progress_0.setValue(int(v['ask_size']*100))
        self.btn_0.setText(f"{v['ask_price']:,}")
        self.btn_0.clicked.connect(lambda: self.clicked_orderchart(self.btn_0))

        v = data['orderbook_units'][2]
        # self.order_10.setText(f"{v['ask_price']:,}")
        self.order_11.setText(f"{v['ask_size']:,}")
        self.order_12.setText(f"{v['ask_price'] * v['ask_size']}")
        self.order_progress_1.setRange(0, max_size)
        self.order_progress_1.setValue(int(v['ask_size']*100))
        self.btn_1.setText(f"{v['ask_price']:,}")
        self.btn_1.clicked.connect(lambda: self.clicked_orderchart(self.btn_1))

        v = data['orderbook_units'][1]
        # self.order_20.setText(f"{v['ask_price']:,}")
        self.order_21.setText(f"{v['ask_size']:,}")
        self.order_22.setText(f"{v['ask_price'] * v['ask_size']}")
        self.order_progress_2.setRange(0, max_size)
        self.order_progress_2.setValue(int(v['ask_size']*100))
        self.btn_2.setText(f"{v['ask_price']:,}")
        self.btn_2.clicked.connect(lambda: self.clicked_orderchart(self.btn_2))

        v = data['orderbook_units'][0]
        # self.order_30.setText(f"{v['ask_price']:,}")
        self.order_31.setText(f"{v['ask_size']:,}")
        self.order_32.setText(f"{v['ask_price'] * v['ask_size']}")
        self.order_progress_3.setRange(0, max_size)
        self.order_progress_3.setValue(int(v['ask_size']*100))
        self.btn_3.setText(f"{v['ask_price']:,}")
        self.btn_3.clicked.connect(lambda: self.clicked_orderchart(self.btn_3))
        
        v = data['orderbook_units'][0]
        # self.order_40.setText(f"{v['bid_price']:,}")
        self.order_41.setText(f"{v['bid_size']:,}")
        self.order_42.setText(f"{v['bid_price'] * v['bid_size']}")
        self.order_progress_4.setRange(0, max_size)
        self.order_progress_4.setValue(int(v['bid_size']*100))
        self.btn_4.setText(f"{v['bid_price']:,}")
        self.btn_4.clicked.connect(lambda: self.clicked_orderchart(self.btn_4))

        v = data['orderbook_units'][1]
        # self.order_50.setText(f"{v['bid_price']:,}")
        self.order_51.setText(f"{v['bid_size']:,}")
        self.order_52.setText(f"{v['bid_price'] * v['bid_size']}")
        self.order_progress_5.setRange(0, max_size)
        self.order_progress_5.setValue(int(v['bid_size']*100))
        self.btn_5.setText(f"{v['bid_price']:,}")
        self.btn_5.clicked.connect(lambda: self.clicked_orderchart(self.btn_5))

        v = data['orderbook_units'][2]
        # self.order_60.setText(f"{v['bid_price']:,}")
        self.order_61.setText(f"{v['bid_size']:,}")
        self.order_62.setText(f"{v['bid_price'] * v['bid_size']}")
        self.order_progress_6.setRange(0, max_size)
        self.order_progress_6.setValue(int(v['bid_size']*100))
        self.btn_6.setText(f"{v['bid_price']:,}")
        self.btn_6.clicked.connect(lambda: self.clicked_orderchart(self.btn_6))

        v = data['orderbook_units'][3]
        # self.order_70.setText(f"{v['bid_price']:,}")
        self.order_71.setText(f"{v['bid_size']:,}")
        self.order_72.setText(f"{v['bid_price'] * v['bid_size']}")
        self.order_progress_7.setRange(0, max_size)
        self.order_progress_7.setValue(int(v['bid_size']*100))
        self.btn_7.setText(f"{v['bid_price']:,}")
        self.btn_7.clicked.connect(lambda: self.clicked_orderchart(self.btn_7))

    def clicked_orderchart(self, e):
        self.lineEdit_4.setText(e.text())

    def chart_widget(self, ticker='KRW-BTC'): # for chart
        self.ticker = ticker
        self.viewLimit = 128

        self.pw = PriceWorker(ticker)
        self.pw.priceDataSent.connect(self.append_chart_data)
        self.pw.start()

    def append_chart_data(self, df): # for chart
        self.ticks = Series(dtype='float64') 
        dt = QDateTime.currentDateTime()

        self.series = QCandlestickSeries()
        self.series.setIncreasingColor(Qt.red)
        self.series.setDecreasingColor(Qt.blue)

        for index in df.index:
            open = df.loc[index, 'open']
            high = df.loc[index, 'high']
            low = df.loc[index, 'low']
            close = df.loc[index, 'close']

            # time conversion
            format = "%Y-%m-%d %H:%M:%S"
            str_time = index.strftime(format)
            dt = QDateTime.fromString(str_time, "yyyy-MM-dd hh:mm:ss")
            ts = dt.toMSecsSinceEpoch()
            #ts = index.timestamp() * 1000
            #print(ts)

            elem = QCandlestickSet(open, high, low, close, ts)
            self.series.append(elem)
                # chart object
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(self.series)         # data feeding

        # axis
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm:ss")
        chart.addAxis(axis_x, Qt.AlignBottom)
        self.series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.series.attachAxis(axis_y)

        # margin
        chart.layout().setContentsMargins(0, 0, 0, 0)

        # displaying chart
        self.priceView.setChart(chart)
        self.priceView.setRenderHint(QPainter.Antialiasing)
        # self.setCentralWidget(self.priceView)

    def append_article_data(self, data):
        print('append_article_data :', data)
        if data == None:
            return
        if 'init_article_list' in data:
            self.article_db['article_list'] = data['init_article_list']
            articles_day_rowCount = 0
            self.articles_day.clear()
            for i in range(self.articles_day.rowCount()):
                self.articles_day.removeRow(0)

            for idx, row  in data['init_article_list'].iterrows():
                print('== init_article_list row :', row)
                self.articles_day.insertRow(articles_day_rowCount)
                buf = QTableWidgetItem(str(row['date']))
                buf.setTextAlignment(Qt.AlignHCenter)
                self.articles_day.setItem(articles_day_rowCount, 0, buf)
                self.articles_day.setItem(articles_day_rowCount, 1, QTableWidgetItem(str(row['title'])))
                buf = QTableWidgetItem(str(row['accuracy']))
                buf.setTextAlignment(Qt.AlignHCenter)
                self.articles_day.setItem(articles_day_rowCount, 2, buf)
                articles_day_rowCount += 1
                
        elif 'init_buy_sell_list' in data:
            self.article_db['buy_sell_list'] = data['init_buy_sell_list']
            buy_sell_rowCount = 0
            self.buy_sell.clear()
            for i in range(self.buy_sell.rowCount()):
                self.buy_sell.removeRow(0)
            print('== init_buy_sell_list row :', data)
            for row  in data['init_buy_sell_list']:
                self.buy_sell.insertRow(buy_sell_rowCount)
                if row['transaction'] == '매수':
                    font = QTableWidgetItem(str(row['transaction']))
                    font.setForeground(QBrush(QColor(255, 0, 0)))
                    self.buy_sell.setItem(buy_sell_rowCount, 2, font)
                else:
                    font = QTableWidgetItem(str(row['transaction']))
                    font.setForeground(QBrush(QColor(0, 0, 255)))
                    self.buy_sell.setItem(buy_sell_rowCount, 2, font)
                self.buy_sell.setItem(buy_sell_rowCount, 0, QTableWidgetItem(str(row['date'])))
                self.buy_sell.setItem(buy_sell_rowCount, 1, QTableWidgetItem(str(row['ticker'])))
                # self.buy_sell.setItem(buy_sell_rowCount, 2, QTableWidgetItem(str(row['transaction'])))
                self.buy_sell.setItem(buy_sell_rowCount, 3, QTableWidgetItem(str(row['krw_amount'])))
                self.buy_sell.setItem(buy_sell_rowCount, 4, QTableWidgetItem(str(row['ticker_amount'])))
                buy_sell_rowCount += 1
        
    def inDetailBtn(self): # 자세히 보기 버튼
        print('자세히 보기 버튼 클릭!')
        # self.ai_window.show()

    def article_init(self):
        self.articles_day.setColumnWidth(0, int(self.articles_day.width()*0.2))
        self.articles_day.setColumnWidth(1, int(self.articles_day.width()*0.7))
        self.articles_day.setColumnWidth(2, int(self.articles_day.width()*0.08))
        self.articles_contents.setColumnWidth(0, int(self.articles_day.width()*0.75))
        self.articles_contents.setColumnWidth(1, int(self.articles_day.width()*0.05))
        self.articles_contents.setColumnWidth(2, int(self.articles_day.width()*0.05))
        self.ai = AiThread()
        self.article_db = dict()
        self.ai_thread_command.connect(self.ai.set_command)
        self.ai.article_data.connect(self.append_article_data)
        self.ai.alive = True
        self.ai.start()
        command = {'command' : 'init_article_list', 'content' : None,}
        self.ai_thread_command.emit(command)
        time.sleep(1)
        command = {'command' : 'init_buy_sell_list', 'content' : None,}
        self.ai_thread_command.emit(command)

        # self.tk = Tokenizer()
        # self.tk.fit_on_texts(self.X_train)
        # self.max_len = 14
        # self.model = load_model('First_model.h5')

        self.title_result = int()

        # self.articles_contents.itemDoubleClicked.connect(self.analysis_sentence)
        self.articles_day.itemDoubleClicked.connect(self.append_articles_contents_table)

    def append_articles_contents_table(self):
        # Append 1 row to the articles_contents table
        for i in range(self.articles_contents.rowCount()):
            self.articles_contents.removeRow(0)
        self.articles_contents.clearContents()
        articles_contents_rowCount = 0
        index = self.articles_day.currentRow()
        texts = self.article_db['article_list'][index]['contents'].split('. ')
        for row  in texts:
            self.articles_contents.insertRow(articles_contents_rowCount)
            self.articles_contents.setItem(articles_contents_rowCount, 0, QTableWidgetItem(str(row)))
            articles_contents_rowCount += 1
        self.articles_contents.resizeRowsToContents()


if __name__== '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())