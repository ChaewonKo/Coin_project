import sys, time, pybithumb, pyupbit, requests, re
from bs4 import BeautifulSoup
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QProgressBar, QApplication, QMainWindow, QBoxLayout, QLabel, QListWidgetItem
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal, QPropertyAnimation
from konlpy.tag import Okt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from mpl_finance import candlestick_ohlc
# from tensorflow.keras.preprocessing.text import Tokenizer
from pandas import Series

main_ui = uic.loadUiType("resources/main.ui")[0]
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

class Item(QWidget):
    def __init__(self, ticker, list_type):
        QWidget.__init__(self, flags=Qt.Widget)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.ticker = ticker
        layout.addWidget(QLabel(self.ticker[list_type]))
        layout.addWidget(QLabel(self.ticker['market']))
        self.setLayout(layout)



class MainWindow(QMainWindow, main_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = 'KRW-BTC'
        # self.upbit = pyupbit()
        self.tickers_list_widget()
        self.chart_widget()
        self.orderbook_widget()
        self.ai_trade_widget()
        
        
        self.pushButton.clicked.connect(self.inDetailBtn)
        self.pushButton_2.clicked.connect(self.AiStart)

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

        self.lineEdit_3.setText(ticker.ticker['korean_name'])

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
                QProgressBar {background-color : rgba(0, 0, 0, 0);border : 1;font: 9px;height: 6px;}
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

        self.pw = PriceWorker(ticker)
        self.pw.priceDataSent.connect(self.appendData)
        self.pw.start()

    def appendData(self, df): # for chart
        self.ticks = Series(dtype='float64') 
        dt = QDateTime.currentDateTime()

        self.series = QCandlestickSeries()
        self.series.setIncreasingColor(Qt.red)
        self.series.setDecreasingColor(Qt.blue)
        # for i in currPrice.iteritems():
        #     print(i[1])
        # print('Time :', dt)
        # print('Data :', df)
        # print('priceData :', df['close'][1])

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

    def ai_trade_widget(self):
        self.ai_window = AiWindow(self)
        self.ai = AiThread(self)
        


    def inDetailBtn(self): # 자세히 보기 버튼
        print('자세히 보기 버튼 클릭!')
        self.ai_window.show()
    
    def AiStart(self): # 자동 거래 시작
        print('Clicked Aistart button!')

from datetime import date, datetime
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import random
import pandas
ai_ui = uic.loadUiType("resources/ai.ui")[0]

class AiWindow(QMainWindow, ai_ui):
    def __init__(self, parent=None):
        super(AiWindow, self).__init__(parent)
        self.okt = Okt()
        self.setupUi(self)
        self.get_first_index()
        self.article_content = list()
        self.X_train = list()
        f = open('Datas/X_train.txt', 'r')
        while True:
            a = f.readline()
            if not a:
                break
            text = a.split(' ')
            self.X_train.append(text)
        # print(self.X_train)
        self.tk = Tokenizer()
        self.tk.fit_on_texts(self.X_train)
        self.max_len = 14
        self.model = load_model('First_model.h5')

        self.title_result = int()
        



        # self.articles_contents.itemDoubleClicked.connect(self.analysis_sentence)
        self.articles_day.itemDoubleClicked.connect(self.append_articles_contents_table)

        self.articles_day.setColumnWidth(0, int(self.articles_contents.width()*0.12))
        self.articles_day.setColumnWidth(1, int(self.articles_contents.width()*0.65))
        self.articles_day.setColumnWidth(2, int(self.articles_contents.width()*0.09))
        self.articles_day.setColumnWidth(3, int(self.articles_contents.width()*0.09))
        self.get_buy_sell()
        self.get_article()

    def get_buy_sell(self):
        df = pandas.read_csv('Datas/buy_sell_list.csv')
        buy_sell_rowCount = self.buy_sell.rowCount()
        for index, row  in df.iterrows():
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

    def get_first_index(self):
        url = 'https://kr.coinness.com/'
        article = requests.get(url=url)
        article = BeautifulSoup(article.text, 'html.parser')
        index_data = article.select('#index > div.nno > div.fl > div > div.home-container > div:nth-of-type(2) > div.content-wrap > ul > li:nth-of-type(1) > div > a')
        self.first_index = int(re.sub(r'[^0-9]', '', index_data[0]['href'])) # 사이트의 가장 최근 기사의 인덱스를 가져옴
        print('first index :', self.first_index)

    def get_article(self):
        today = [datetime.today().year, datetime.today().month, datetime.today().day]
        for index in range(self.first_index, 0, -2):
            url = "https://kr.coinness.com/news/" + str(index)
            article = requests.get(url=url)
            article = BeautifulSoup(article.text, 'html.parser')
            article_title = article.select('#detail > div > div.fl > div > section > h2')
            article_title = article_title[0].text

            article_date = article.select('#detail > div > div.fl > div > section > div > div.time > span.month')
            article_date = article_date[0].text
            article_date = [d for d in article_date.split(' ') if d and d != '\n']

            article_content = article.select('#detail > div > div.fl > div > section > div > div.content')
            self.article_content.append([sentence for sentence in article_content[0].text.split('.') if sentence])
            for i, v in enumerate(today):
                if str(v) != re.sub(r'[^0-9]', '', article_date[i]): # 기사의 날짜가 오늘과 다르면 끝
                    return
            
            self.append_articles_day_table(date=article_date, title=article_title)
            # self.append_articles_contents_table(contents=self.article_content[-1])

            # time.sleep(1)


        
    def append_articles_day_table(self, date, title):
        # Append 1 row to the articles_day table
        articles_day_rowCount = self.articles_day.rowCount()
        self.articles_day.insertRow(articles_day_rowCount)
        
        self.articles_day.setItem(articles_day_rowCount, 0, QTableWidgetItem('-'.join(date[:3])))
        self.articles_day.setItem(articles_day_rowCount, 1, QTableWidgetItem(title))


    def append_articles_contents_table(self, item):
        contents = self.article_content[item.row()]
        # Append 1 row to the articles_contents table
        self.articles_contents.clearContents()
        articles_contents_rowCount = 0
        for i, v in enumerate(contents):
            self.articles_contents.insertRow(articles_contents_rowCount)
            articles_contents_rowCount += 1
            self.articles_contents.setItem(i, 0, QTableWidgetItem(v))
            # print('result 0 :', v)
            # v_result = self.tk.texts_to_sequences(v)
            # print('result 1 :', v_result)
            # v_result = pad_sequences(v_result, maxlen=self.max_len)
            # print('result 2 :', v_result)
            # result = self.model.predict_classes(v_result)
            # print('result 3 :', v_result)
            p = random.randint(0, 2) - 1
            if p:
                font = QTableWidgetItem('긍정')
                font.setForeground(QBrush(QColor(0, 255, 0)))
                self.articles_contents.setItem(i, 1, font)
            else:
                font = QTableWidgetItem('부정')
                font.setForeground(QBrush(QColor(255, 0, 0)))
                self.articles_contents.setItem(i, 1, font)
            # print(i, ' :', v)

        height = int(self.articles_contents.height() / 5) # pixel
        for i in range(articles_contents_rowCount):
            self.articles_contents.setRowHeight(i, height)
        
    def append_text_flow_table(self, data):
        # Append text_flow table
        text_flow_columnCount = 0
        for i, v in enumerate(data):
            self.text_flow.insertColumn(text_flow_columnCount)
            text_flow_columnCount += 1
            self.text_flow.setItem(0 , i, QTableWidgetItem(v))

        width = int((self.text_flow.width()-40 ) / text_flow_columnCount) # pixel
        for i in range(text_flow_columnCount):
            self.text_flow.setColumnWidth(i, width)

    def analysis_sentence(self, item):
        # print('item :', item.text())
        data = self.okt.nouns(item.text())
        # print('data :', data)
        self.append_text_flow_table(data=data)

class AiThread(QThread):
    # dataSent = pyqtSignal(dict)

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

if __name__== '__main__':
    app = QApplication(sys.argv)

    if len(sys.argv)-1 and str(sys.argv[1]) =='detail':
        buf = AiWindow()
        buf.show()
    else :
        mw = MainWindow()
        mw.show()

    exit(app.exec_())