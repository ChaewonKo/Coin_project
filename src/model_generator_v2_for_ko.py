import re
import pandas as pd
from pandas.core.frame import DataFrame
import pyupbit
from multiprocessing import Pool
import numpy as np
from konlpy.tag import Okt

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score


class Model_generator_ko():
    def __init__(self) -> None:
        self.data_path = r'../Datas/train copy.csv'
        self.data_db = pd.read_csv(self.data_path, delimiter=',')
        self.okt = Okt()

    def main(self):
        normalized_data = self.data_db['contents'].apply(self.normalize_reviews)
        ''' cloudword 출력용
        clean_data_list = normalized_data.tolist()
        normalized_data = ' '.join(clean_data_list)
        print('== Noun list :', type(normalized_data))
        self.displayWordCloud(data = normalized_data)
        '''
        normalized_data = normalized_data.to_list()
        # 문자열의 길이 구하기
        # clean_data_list = normalized_data.apply(lambda x: len(str(x).split()))

        vectorizer = CountVectorizer(
            lowercase=False,
            analyzer='word',
            tokenizer=None,
            preprocessor=None,
            stop_words=None,
            min_df=2,  # 토큰이 나타날 최소 문서 개수
            ngram_range=(1, 3),
            max_features=20000)
        print('== Vectorizer')
        print(vectorizer)
        pipeline = Pipeline([
            ('vect', vectorizer),
        ])
        train_data_features = pipeline.fit_transform(normalized_data)
        print('== train_data_features :')
        print(train_data_features)
        # print(train_data_features.shape)

        vocab = vectorizer.get_feature_names()
        print('== vocab')
        print(len(vocab))
        print(vocab[:10])

        print('== 벡터화된 피처')
        dist = np.sum(train_data_features, axis=0)
        for tag, count in zip(vocab, dist):
            print(count, tag)
        buf = pd.DataFrame(dist, columns=vocab)
        print(buf)

        print('== forest')
        forest = RandomForestClassifier(
            n_estimators = 100,
            n_jobs = -1,
            random_state=2018)
        print(forest)

        print('== Fit')
        forest.fit(train_data_features, self.data_db['evaluation'])
        print('== Score')
        print('== X_train :', train_data_features)
        Y_train =self.data_db['evaluation'].to_list()
        print('== Y_train :', Y_train)
        buf_score = cross_val_score(
            estimator=forest, 
            X=train_data_features,
            y=Y_train,
            groups=2,
            # cv=10,
            scoring='roc_auc')
        print('== Mean')
        score = np.mean(buf_score)
        print('== score')
        print(score)



    def normalize_reviews(self, data):
        # print('== Data :', data)
        data = re.sub('[^가-힣]', '', data, flags=re.MULTILINE)
        if data and type(data) == str:
            data = self.okt.nouns(data)
            return ' '.join(data)
        else:
            return ' '

    def displayWordCloud(self, data, backgroundcolor = 'white', width=800, height=600):
        print('In display data', data)
        wordcloud = WordCloud(
            stopwords=None,
            background_color = backgroundcolor, 
            width = width, height = height,
            font_path=r'‪C:\Windows\Fonts\HMKMAMI.TTF').generate(data)
        wordcloud.to_file('word_cloud_new.png')
        plt.figure(figsize = (15 , 10))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show() 
    
    def review_to_words(self, raw_review ):
        print('raw_revice :', raw_review)
        # 1. HTML 제거
        # review_text = BeautifulSoup(raw_review, 'html.parser').get_text()
        # 2. 영문자가 아닌 문자는 공백으로 변환
        # letters_only = re.sub('[^a-zA-Z]', ' ', review_text)
        # 3. 소문자 변환
        # words = letters_only.lower().split()
        # 4. 파이썬에서는 리스트보다 세트로 찾는게 훨씬 빠르다.
        # stopwords 를 세트로 변환한다. 
        # stops = set(stopwords.words('english'))

        # print('형태소 추출 전')
        # print(raw_review)
        # words = self.okt.normalize(self, phrase=raw_review)
        # print('정규화 :')
        words = self.okt.nouns(raw_review)
        # print(words)
        self.stopswords_path = r'../Datas/stopwords_ko.txt'

        with open(self.stopswords_path, 'r', encoding='UTF8') as f:
            stops = f.read().split('\n')
        
        # print('보여주기 :', stops)
        # 5. Stopwords 불용어 제거
        meaningful_words = [w for w in words if not w in stops]
        # print('보여주기 :', meaningful_words)
        # 6. 어간추출
        # stemming_words = [stemmer.stem(w) for w in meaningful_words]
        # # 7. 공백으로 구분된 문자열로 결합하여 결과를 반환
        # return( ' '.join(stemming_words) )
        print(meaningful_words)
        return(' '.join(meaningful_words) )

    def _apply_df(self, args):
        df, func, kwargs = args
        print('===============')
        print('df :', df)
        print('func :', func)
        print('kwargs :', kwargs)
        return df.apply(func, **kwargs)

    def apply_by_multiprocessing(self, df, func, **kwargs):
        # 키워드 항목 중 workers 파라메터를 꺼냄
        workers = kwargs.pop('workers')
        # 위에서 가져온 workers 수로 프로세스 풀을 정의
        pool = Pool(processes=workers)
        # 실행할 함수와 데이터프레임을 워커의 수 만큼 나눠 작업
        a = [(d, func, kwargs) for d in np.array_split(df, workers)]
        result = pool.map(self._apply_df, a)
        pool.close()
        # 작업 결과를 합쳐서 반환
        return pd.concat(list(result))

    def update_BTC_price(self): # 데이터 생성을 위한 함수
        data_file = r'../Datas/BTC_price.csv'
        df = pyupbit.get_ohlcv("KRW-BTC")
        buf_dict = pd.DataFrame([], columns = ['Date' , 'Price'])
        yesterday_price = 0
        for index, item in df.iterrows():
            if yesterday_price == 0:
                yesterday_price = item['close']
                continue
            if item['close'] > yesterday_price:
                buf = 1
            elif item['close'] < yesterday_price:
                buf = -1
            else:
                buf = 0
            buf_dict = buf_dict.append({'Date' : index.strftime('%Y-%m-%d'), 'Price' :str(buf)}, ignore_index=True)
            yesterday_price = item['close']
        buf_dict.to_csv(data_file, index=False)



        

if __name__=='__main__':
    Mg = Model_generator_ko()
    Mg.main()
    # Mg.update_BTC_price()