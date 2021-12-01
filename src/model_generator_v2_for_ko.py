import re, pickle, time
from nltk import translate
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import pyupbit
from multiprocessing import Pool
import numpy as np

from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from google.cloud import translate
class Model_generator_ko():
    def __init__(self) -> None:
        self.data_path = r'../Datas/train.csv'
        self.data_db = pd.read_csv(self.data_path, delimiter=',')
        # self.translator = googletrans.Translator()
        self.stemmer = SnowballStemmer('english')

    def main(self):
        self.data_db['contents_en'] = self.data_db['contents'].apply(self.review_to_words)
        self.data_db.to_csv(r'../Datas/train_ko2en.csv', index=False)
        # clean_train_reviews = self.apply_by_multiprocessing(
        #     self.data_db['contents'], self.review_to_words, workers=4)
        
        ''' # cloudword 출력용
        clean_data_list = clean_train_reviews.tolist()
        normalized_data = ' '.join(clean_data_list)
        self.displayWordCloud(data = normalized_data)

        return
        '''

        vectorizer = CountVectorizer(
            lowercase=False,
            analyzer='word',
            tokenizer=None,
            preprocessor=None,
            stop_words=None,
            min_df=2,  # 토큰이 나타날 최소 문서 개수
            ngram_range=(1, 3),
            max_features=20000)

        pipeline = Pipeline([('vect', vectorizer)])

        train_data_features = pipeline.fit_transform(clean_train_reviews)
        # print(train_data_features.shape)

        vocab = vectorizer.get_feature_names()

        dist = np.sum(train_data_features, axis=0)
        for tag, count in zip(vocab, dist):
            print(count, tag)
        buf = pd.DataFrame(dist, columns=vocab)

        forest = RandomForestClassifier(
            n_estimators=100,
            n_jobs=-1,
            random_state=2018)

        forest.fit(train_data_features, self.data_db['evaluation'])
        print('== Score')
        print('== X_train :', train_data_features)
        Y_train = self.data_db['evaluation'].to_list()
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

        pickle.dump(forest, open('finalized_model_ko.sav', 'wb'))
        pickle.dump(vectorizer, open("vectorizer_ko.pickle", "wb"))
            
    def review_to_words(self, data):
        translator = googletrans.Translator()
        translator.raise_Exception = True

        # translate = translator.translate()

        # 1. 한국어를 영어로 번역
        raw_review = translator.translate(data, src='ko', dest='en').text
        # print('Data :', raw_review)
        # 2. 영문자가 아닌 문자는 공백으로 변환
        print('== Data :', raw_review)
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

    def displayWordCloud(self, data, backgroundcolor='white', width=800, height=600):
        wordcloud = WordCloud(
            stopwords=None,
            background_color=backgroundcolor,
            width=width, height=height,
            font_path=r'‪C:\Windows\Fonts\HMKMAMI.TTF').generate(data)
        wordcloud.to_file('word_cloud_ko2en.png')
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()

    def _apply_df(self, args):
        df, func, kwargs = args
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

    def update_BTC_price(self):  # 데이터 생성을 위한 함수
        data_file = r'../Datas/BTC_price.csv'
        df = pyupbit.get_ohlcv("KRW-BTC")
        buf_dict = pd.DataFrame([], columns=['Date', 'Price'])
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
            buf_dict = buf_dict.append({'Date': index.strftime(
                '%Y-%m-%d'), 'Price': str(buf)}, ignore_index=True)
            yesterday_price = item['close']
        buf_dict.to_csv(data_file, index=False)


if __name__ == '__main__':
    Mg = Model_generator_ko()
    Mg.main()
    # Mg.update_BTC_price()
