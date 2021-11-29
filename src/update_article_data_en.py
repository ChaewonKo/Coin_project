from bs4 import BeautifulSoup
from datetime import datetime
import time, random, json, pickle
import numpy as np
from pandas.core.frame import DataFrame
import requests, re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
# from tensorflow.python.keras.preprocessing.text import Tokenizer
# from keras.models import load_model

from sklearn.pipeline import Pipeline


class Crawling_data_en():
    def __init__(self):
        self.data_base = pd.DataFrame(columns=['id', 'date', 'evaluation', 'accuracy', 'title', 'contents'])
        self.first_index = int()
        self.latest_index = int()
        self.saved_latest_index = int()
        self.file_path = r'../Datas/train_en.csv'
        self.data_base = pd.read_csv(self.file_path, delimiter=',')
        self.evaluation_file_path = r'../Datas/BTC_price.csv'
        self.evaluation_per_date = pd.read_csv(self.evaluation_file_path, delimiter=',')
        self.evaluation_per_date = self.evaluation_per_date.set_index('Date').to_dict()
        self.get_first_index()
        self.set_saved_latest_index()
        self.loaded_model  = pickle.load(open('finalized_model.sav', 'rb'))
        self.vertorize = pickle.load(open("vectorizer.pickle", 'rb'))  
        self.stemmer = SnowballStemmer('english')

    def main(self):
        while True:
            if self.first_index > self.saved_latest_index:
                self.get_article(self.first_index, self.file_path)
                self.set_saved_latest_index()
            break

            time.sleep(1)


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
            break


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
            print('sentence :', sentence)
            
            clean_test_reviews = sentence['contents'].apply(self.review_to_words)
            print('clean_test_reviews :', clean_test_reviews[0])
            print('clean_test_reviews :', type(clean_test_reviews[0]))
            test_data_features = self.vertorize.transform(clean_test_reviews)
            test_data_features = test_data_features.toarray()
            print('test_data_features :', test_data_features)
            result = self.loaded_model.predict(test_data_features)
        print(result)
        
        if result > 0.7:
            judge = 'up'
        elif result < 0.3:
            judge = 'down'
        else:
            judge = 'unknown'
        
        return result, judge
    
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
    # C.main()
    ''' 스코어 함수 테스트용
    '''
    data = np.array([[3, ' According to the authors of the report users of metaverse-based wallets have increased by 10x since the beginning of the year to around 50000 active wallets. It continued that the space though still very much new could become mainstream in the coming years if it continues with its current growth trajectory.']])
    sentence = pd.DataFrame(data, columns=['id', 'contents']) 
    print(C.get_score(sentence=sentence))
    ''' 학습용으로 저장된 데이터의 evaluation과 accuracy를 날짜에 맞는 값을 넣어줌
    C.for_changing_data_with_score()
    '''