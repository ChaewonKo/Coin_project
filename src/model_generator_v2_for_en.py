from os import pipe
import re, pickle
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import pandas as pd

from multiprocessing import Pool
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score


class Model_generator_en():
    def __init__(self) -> None:
        self.data_path = r'../Datas/train_en.csv'
        self.data_db = pd.read_csv(self.data_path, delimiter=',')
        self.train = pd.read_csv(r'../Datas/labeledTrainData.tsv', delimiter='\t', quoting=3)
        self.stemmer = SnowballStemmer('english')

    def main(self):
        clean_train_reviews = self.apply_by_multiprocessing(
            self.train['review'], self.review_to_words, workers=4)

        vectorizer = CountVectorizer(
            analyzer='word',
            tokenizer=None,
            preprocessor=None,
            stop_words=None,
            min_df=2,  # 토큰이 나타날 최소 문서 개수
            ngram_range=(1, 3),
            max_features=20000)

        pipeline = Pipeline([('vect', vectorizer)])
        print('pipeline :', pipeline)

        train_data_features = pipeline.fit_transform(clean_train_reviews)

        vocab = vectorizer.get_feature_names_out()

        forest = RandomForestClassifier(
            n_estimators=100, n_jobs=-1, random_state=2018)

        forest = forest.fit(train_data_features, self.train['sentiment'])



        buf = cross_val_score(
            forest, 
            train_data_features,
            self.train['sentiment'],
            cv=10, 
            scoring='roc_auc')

        print('buf :', buf)
        pickle.dump(forest, open('finalized_model.sav', 'wb'))
        pickle.dump(vectorizer, open("vectorizer.pickle", "wb"))



    def review_to_words(self, raw_review):
        # 1. HTML 제거
        review_text = BeautifulSoup(raw_review, 'html.parser').get_text()
        # 2. 영문자가 아닌 문자는 공백으로 변환
        letters_only = re.sub('[^a-zA-Z]', ' ', review_text)
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

    def _apply_df(self, args):
        df, func, kwargs = args
        return df.apply(func, **kwargs)

    def apply_by_multiprocessing(self, df, func, **kwargs):
        # 키워드 항목 중 workers 파라메터를 꺼냄
        workers = kwargs.pop('workers')
        # 위에서 가져온 workers 수로 프로세스 풀을 정의
        pool = Pool(processes=workers)
        # 실행할 함수와 데이터프레임을 워커의 수 만큼 나눠 작업
        result = pool.map(self._apply_df, [(d, func, kwargs) for d in np.array_split(df, workers)])
        pool.close()
        # 작업 결과를 합쳐서 반환
        return pd.concat(list(result))


if __name__ == '__main__':
    Mg = Model_generator_en()
    Mg.main()
    # Mg.update_BTC_price()
