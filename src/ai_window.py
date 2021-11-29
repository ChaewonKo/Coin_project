from datetime import date, datetime
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
# from keras.models import load_model
import random
from PyQt5 import uic
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from bs4 import BeautifulSoup
from konlpy.tag import Okt
import pandas
import requests
from tensorflow.python.keras.preprocessing.text import Tokenizer
from keras.models import load_model

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
        url = 'https://www.tokenpost.kr/articles'
        req = requests.get(url=url)
        soup = BeautifulSoup(req.text, 'html.parser')
        index_data = soup.select('#list > div > div:nth-of-type(1) > div > div.articleListTitle.marginB8 > a')
        # print('index_data :', index_data)
        self.first_index = int(re.sub(r'[^0-9]', '', index_data[0]['href'])) # 사이트의 가장 최근 기사의 인덱스를 가져옴
        # print('first index :', self.first_index)

    def get_article(self):
        today = '{}-{}-{}'.format(datetime.today().year, datetime.today().month, datetime.today().day)
        print('첫 인덱스:', self.first_index)
        for index in range(self.first_index, 0, -1):
            url = "https://www.tokenpost.kr/article-" + str(index)
            article = requests.get(url=url)
            article = BeautifulSoup(article.text, 'html.parser')
            article_title = article.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewArticleTitle > p')
            article_title = article_title[0].text
            print('인덱스 :', index)
            print('기사 제목 :', article_title.lstrip().rstrip())

            article_date = article.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewRow > div.viewArticleInfo > div.viewInfoLeft > div > p')
            article_date = article_date[0].text
            article_date = [d for d in article_date.split(' ') if d and d != '\n']
            print('기사 날짜 :', article_date)

            article_content = article.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewArticle > p')
            self.article_content.append([sentence for sentence in article_content[0].text.split('.') if sentence])

            print('날짜 비교 : {}, {}'.format(article_date[0], today))
            if str(article_date[0]) != today: # 기사의 날짜가 오늘과 다르면 끝
                break


        
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