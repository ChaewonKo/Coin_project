from bs4 import BeautifulSoup
from datetime import datetime
import time, random
import requests, re
import pandas as pd
from tensorflow.python.keras.preprocessing.text import Tokenizer
from keras.models import load_model


class Crawling_data_Ko():
    def __init__(self):
        # self.data_base = pd.DataFrame(columns=['date', 'id', 'title', 'evaluation', 'accuracy', 'contents'])
        self.first_index = int()
        self.latest_index = int()
        self.saved_latest_index = int()
        self.file_path = r'../Datas/articles_one_day.csv'
        self.data_base = pd.read_csv(self.file_path, delimiter=',')
        self.evaluation_file_path = r'../Datas/BTC_price.csv'
        self.evaluation_per_date = pd.read_csv(self.evaluation_file_path, delimiter=',')
        self.evaluation_per_date = self.evaluation_per_date.set_index('Date').to_dict()
        self.set_saved_latest_index()

    def main(self):
        while True:
            self.get_first_index()
            if self.first_index > self.saved_latest_index:
                self.get_article(self.first_index, self.file_path)
                self.set_saved_latest_index()

            time.sleep(1)


    def get_first_index(self):
        url = 'https://www.tokenpost.kr/articles'
        req = requests.get(url=url)
        soup = BeautifulSoup(req.text, 'html.parser')
        index_data = soup.select('#list > div > div:nth-of-type(1) > div > div.articleListTitle.marginB8 > a')
        self.first_index = int(re.sub(r'[^0-9]', '', index_data[0]['href'])) # 사이트의 가장 최근 기사의 인덱스를 가져옴
        print('first index :', self.first_index)

    def get_article(self, new_index, file_path):
        # today = '{}-{}-{}'.format(datetime.today().year, datetime.today().month, datetime.today().day)
        count = 0
        print('인덱스 비교', new_index, self.saved_latest_index)
        for index in range(self.saved_latest_index, new_index):
            article = pd.Series([],dtype=pd.StringDtype()) 
            url = "https://www.tokenpost.kr/article-" + str(index)
            req = requests.get(url=url)
            req = BeautifulSoup(req.text, 'html.parser')

            article_title = req.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewArticleTitle > p')
            if not article_title:
                print('내용이 비었다')
                continue
            article_title = article_title[0].text
            article_title = re.sub(r'[^가-힣| |.]', '', article_title) 
            article_date = req.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewRow > div.viewArticleInfo > div.viewInfoLeft > div > p')
            if not article_date:
                print('내용이 비었다')
                continue
            article_date = article_date[0].text
            article_date = [d for d in article_date.split(' ') if d and d != '\n']
            article_content = req.select('#view > div.viewWholeBox > div.viewContent > div.viewContentArticle.noselect > div.viewArticle > p')
            article_content = article_content[0].text
            article_content = re.sub(r'[^가-힣| |.]', '', article_content) 

            # print('인덱스 :', index)
            # print('기사 제목 :', article_title.lstrip().rstrip())
            # print('기사 날짜 :', article_date[0])
            # print('날짜 비교 : {}, {}'.format(article_date[0], today))

            article['date'] = article_date[0] # date
            article['id'] = index # id
            article['title'] = article_title.lstrip().rstrip() # title
            article['evaluation'], article['accuracy'] = self.get_score(
                date=article_date[0],
                for_data_crawling=True ) # evaluation, accuracy
            article['contents'] = row[2] # contents

            # print(article)
            print('데이터 베이스')
            print(self.data_base)
            # print(len(article))
            self.data_base = self.data_base.append(article, ignore_index=True, sort=True).sort_values(by=['id'], axis=0, ascending=False)
            count += 1
            if count > 100:
                break

        print('데이터 베이스 저장!')
        # print(self.data_base)
        self.data_base.to_csv(file_path, index =False)


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
            result = random.random()
        
        if result > 0.7:
            judge = 'up'
        elif result < 0.3:
            judge = 'down'
        else:
            judge = 'unknown'
        
        return result, judge
    
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
    C = Crawling_data_Ko()
    # C.main()
    ''' 스코어 함수 테스트용
    sentence = '美 SEC, 블록파이 조사 들어가…"디파이 업계 본격 옥죄기'
    print(C.get_score(sentence))
    '''
    ''' 학습용으로 저장된 데이터의 evaluation과 accuracy를 날짜에 맞는 값을 넣어줌
    C.for_changing_data_with_score()
    '''