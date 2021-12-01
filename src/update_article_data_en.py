from bs4 import BeautifulSoup
from datetime import datetime
import time, random, json, pickle
import numpy as np
from pandas.core.frame import DataFrame
from pymysql import cursors
import requests, re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
# from tensorflow.python.keras.preprocessing.text import Tokenizer
# from keras.models import load_model

import pymysql
from sklearn.pipeline import Pipeline


class Crawling_data_en():
    def __init__(self):
        self.data_base = pd.DataFrame(columns=['id', 'date', 'evaluation', 'accuracy', 'title', 'contents'])
        self.first_index = int()
        self.latest_index = int()
        self.saved_latest_index = int()
        self.file_path = r'../Datas/train_en.csv'
        self.data_base = pd.read_csv(self.file_path, delimiter=',')
        self.max_index_article = self.data_base['id'].max()
        print('== max_index_article :', self.max_index_article)
        self.evaluation_file_path = r'../Datas/BTC_price.csv'
        self.evaluation_per_date = pd.read_csv(self.evaluation_file_path, delimiter=',')
        self.evaluation_per_date = self.evaluation_per_date.set_index('Date').to_dict()
        # self.get_first_index()
        # self.set_saved_latest_index()
        self.loaded_model  = pickle.load(open('finalized_model_en.sav', 'rb'))
        self.vertorize = pickle.load(open("vectorizer_en.pickle", 'rb'))  
        self.stemmer = SnowballStemmer('english')
        self.sql_db = pymysql.connect(host='118.67.130.16', port=3306, user='manager', passwd='a1s2d3f4!', db='cif', charset='utf8')

    def main(self):
        self.cur = self.sql_db.cursor()
        while True:
            self.request_query()
            # if self.first_index > self.saved_latest_index:
            #     self.get_article(self.first_index, self.file_path)
            #     self.set_saved_latest_index()
            time.sleep(1)

    def request_query(self):
        query_for_index = 'SELECT MAX(cif.trade.t_idx) FROM cif.trade;'
        query = 'SELECT * FROM cif.trade where t_date like \'2021-11-30\';'

        self.cur.execute(query=query_for_index)
        buf_max_index = self.cur.fetchone()[0]

        self.cur.execute(query=query)
        article = pd.Series([], dtype=pd.StringDtype()) 
        print(' self.max_index_article : {}, buf_max_index : {}'.format(self.max_index_article, buf_max_index))
        if self.max_index_article == buf_max_index:
            return

        for row in self.cur:
            # print('== row[0] :', row[0])
            article['date'] = '{}-{}-{}'.format(row[3].year, row[3].month, row[3].day) # date
            article['id'] = row[0] # id
            article['title'] =  re.sub('\,|\n', '', row[5], flags=re.MULTILINE)
            article['evaluation'], article['accuracy'] = self.get_score(
                sentence=row[2]
            )
            article['contents'] = re.sub('\,|\n', '', row[2], flags=re.MULTILINE)
            self.data_base = self.data_base.append(article, ignore_index=True)
            # self.data_base = self.data_base.append(article, ignore_index=True, sort=True).sort_values(by=['id'], axis=0, ascending=False)
        self.data_base.to_csv(self.file_path, index =False)
        self.max_index_article = buf_max_index

    def get_first_index(self):
        url = 'https://www.todayonchain.com/news/'
        req = requests.get(url=url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(req.text, 'html.parser')
        self.first_index = int(soup.find('div', 'api_article shadow-box').attrs['id'])
        print('first index :', self.first_index)

    def get_article(self, new_index, file_path):
        # today = '{}-{}-{}'.format(datetime.today().year, datetime.today().month, datetime.today().day)
        print('인덱스 비교', new_index, self.saved_latest_index)
        url = 'https://www.todayonchain.com/news/'
        req = requests.get(url=url)
        req = BeautifulSoup(req.text, 'html.parser')
        for idx in range(1, 65):
            api_article = req.select('#api-articles > a:nth-of-type({})'.format(idx))
            print('v :', api_article)
            id = api_article[0]
            print('id :', id.find('div', 'api_article.shadow-box'))
            print('=====')

    def set_saved_latest_index(self):
        if len(self.data_base) == 0:
            self.saved_latest_index = 65000
        else:
            self.saved_latest_index = int(self.data_base['id'][0])
        print('저장된 최근 인덱스는? ', self.saved_latest_index)

    def get_score(self, date = None, sentence = None, for_data_crawling = False):
        if for_data_crawling: # 학습용 데이터 수집
            result = self.evaluation_per_date['Price'][date]
        else: # 평가용            
            # clean_test_reviews = sentence['contents'].apply(self.review_to_words)
            clean_test_reviews = self.review_to_words(raw_review=sentence)
            test_data_features = self.vertorize.transform([clean_test_reviews])
            test_data_features = test_data_features.toarray()
            result = self.loaded_model.predict(test_data_features)
        
        if result > 0.7:
            judge = 'up'
        elif result < 0.3:
            judge = 'down'
        else:
            judge = 'unknown'

        print('== result :', result[0])
        print('== judge :', judge)
        
        return result[0], judge
    
    def review_to_words(self, raw_review):
        # 2. 영문자가 아닌 문자는 공백으로 변환
        letters_only = re.sub('[^a-zA-Z]', ' ', raw_review)
        # 3. 소문자 변환
        words = letters_only.lower().split()
        # 4. 파이썬에서는 리스트보다 세트로 찾는게 훨씬 빠르다.
        # stopwords 를 세트로 변환한다.
        stops = set(stopwords.words('english'))
        # 5. Stopwords 불용어 제거
        meaningful_words = [w for w in words if not w in stops]
        # 6. 어간추출
        stemming_words = [self.stemmer.stem(w) for w in meaningful_words]
        # 7. 공백으로 구분된 문자열로 결합하여 결과를 반환
        return(' '.join(stemming_words))

    def for_changing_data_with_score(self):
        print('시작')
        print(self.data_base)
        self.data_base['evaluation'] = self.data_base['date'].apply(self.buf_evaluation)
        self.data_base['accuracy'] = self.data_base['date'].apply(self.buf_accuracy)
        print(self.data_base)
        self.data_base.to_csv(self.file_path, index =False)

    def buf_evaluation(self, date):
        return self.evaluation_per_date['Price'][date]

    def buf_accuracy(self, date):
        result = self.evaluation_per_date['Price'][date]
        if result > 0.7:
            judge = 'up'
        elif result < 0.3:
            judge = 'down'
        else:
            judge = 'unknown'
        return judge


if __name__=='__main__':
    C = Crawling_data_en()
    C.main()
    ''' 스코어 함수 테스트용
    data = np.array([[3, ' According to the authors of the report users of metaverse-based wallets have increased by 10x since the beginning of the year to around 50000 active wallets. It continued that the space though still very much new could become mainstream in the coming years if it continues with its current growth trajectory.']])
    sentence = pd.DataFrame(data, columns=['id', 'contents']) 
    print(C.get_score(sentence=sentence))
    '''
    ''' 학습용으로 저장된 데이터의 evaluation과 accuracy를 날짜에 맞는 값을 넣어줌
    C.for_changing_data_with_score()
    '''