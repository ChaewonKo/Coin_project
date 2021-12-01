from datetime import datetime
import time, random, os
import re
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTableWidgetItem
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tensorflow.python.keras.preprocessing.text import Tokenizer
from keras.models import load_model


class AiThread(QThread):
    article_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__()
        self.alive = False
        self.command = dict()
        self.command_content = dict()
        self.first_index = 0
        self.X_train = list()
        self.file_path_of_articles_list = r'Datas/train_en.csv'
        self.file_path_of_buy_sell_list = r'Datas/buy_sell_list.csv'
        self.mtime_article_list = os.path.getmtime(self.file_path_of_articles_list)
        self.mtime_buy_sell_list = os.path.getmtime(self.file_path_of_buy_sell_list)
        self.today = '{}-{}-{}'.format(datetime.today().year, datetime.today().month, datetime.today().day)


    def run(self):
        while self.alive:
            if self.command == 'init_article_list':
                print('==command :', self.command)
                print('==command_content :', self.command_content)
                print()
                self.init_article_list()
                self.reset_command()
            elif self.command == 'init_buy_sell_list':
                print('==command :', self.command)
                print('==command_content :', self.command_content)
                self.init_buy_sell()
                self.reset_command()
            else :
                print('==command : 업데이트 중')
                print('==command_content :', self.command_content)
                self.update()

            time.sleep(0.5)
    
    def init_article_list(self):
        df = pd.read_csv(self.file_path_of_articles_list)
        print('Df :', df)
        for index, row in df.iterrows():
            print('인덱스 :', index)
            print('내용 :', row['date'])
        print('오늘 날짜 :', self.today)
        sent_data = df.loc[(df['date'] == self.today)]
        print('보낼 데이터 :', sent_data)
        self.article_data.emit({'init_article_list' : sent_data})
        self.mtime_article_list = os.path.getmtime(self.file_path_of_articles_list)

    def article_init(self):
        self.get_first_index()

    def get_first_index(self):
        url = 'https://www.tokenpost.kr/articles'
        req = requests.get(url=url)
        soup = BeautifulSoup(req.text, 'html.parser')
        index_data = soup.select('#list > div > div:nth-of-type(1) > div > div.articleListTitle.marginB8 > a')
        self.first_index = int(re.sub(r'[^0-9]', '', index_data[0]['href'])) # 사이트의 가장 최근 기사의 인덱스를 가져옴
        # print('first index :', self.first_index)
        
    def init_buy_sell(self):
        df = pd.read_csv(self.file_path_of_buy_sell_list)
        # print('== df1 :', df.to_dict('records'))
        self.article_data.emit({'init_buy_sell_list' : df.to_dict('records')})
        self.mtime_buy_sell_list = os.path.getmtime(self.file_path_of_buy_sell_list)

    def update(self):
        buf_article_list = os.path.getmtime(self.file_path_of_articles_list)
        buf_buy_sell = os.path.getmtime(self.file_path_of_buy_sell_list)
        print('최근 기사문 업데이트 시간 :', buf_article_list)
        print('최근 매매 리스트 업데이트 시간 :', buf_buy_sell)
        if self.mtime_buy_sell_list < buf_buy_sell:
            self.init_buy_sell()
        elif self.mtime_article_list < buf_article_list:
            self.init_article_list()

    def change_ticker(self, ticker):
        self.alive = False
        self.ticker = ticker
        self.alive = True

    def set_command(self, command):
        print('==set command!')
        self.command = command['command']
        self.command_content = command['content']

    def reset_command(self):
        print('command reset!')
        self.command  = dict()
        self.command_content = dict()

    def close(self):
        self.alive = False
        self.quit()
        self.wait(5000)
