import pandas as pd
from pandas.core.frame import DataFrame
from tensorflow.keras.preprocessing.text import Tokenizer
from konlpy.tag import Okt
import re
import numpy as np
import matplotlib.pyplot as plt

okt = Okt()
stopwords = ['도', '는', '다', '의', '가', '이', '은', '한', '에', '하', '고', \
    '을', '를', '인', '듯', '과', '와', '네', '들', '듯', '지', '임', '게'] # 불용어 제거

word_data = []
result_data = []

datas = pd.read_csv('Datas/BTC_dataset.csv') # 학습 데이터가 저장된 파일

for data, result in zip(datas['Text'], datas['Price']):
    data = okt.normalize(re.sub(' ', '', data))
    data = okt.morphs(data) # 문장에서 명사를 추출

    word_data.append([word for word in data])
    result_data.append(result)

print('==데이터 수:', len(word_data))
exit

X_train = word_data[:int(len(word_data)/3)] # 학습용 데이터
Y_train = result_data[:int(len(word_data)/3)]
X_test = word_data[-int(len(word_data)/3):] # 평가용 데이터
Y_test = result_data[-int(len(word_data)/3): ]

tk = Tokenizer()
tk.fit_on_texts(X_train)

X_train = tk.texts_to_sequences(X_train)
X_test = tk.texts_to_sequences(X_test)
threshold = 2
word_cnt = len(tk.word_index) + 1
rare_cnt = 0
words_freq = 0
rare_freq = 0

# print('빈도 :', word_cnt)
''' 빈도가 낮은 데이터를 필터하기 위해

for key, value in tk.word_counts.items():
    words_freq = words_freq + value

    if value < threshold:
        rare_cnt += 1
        rare_freq = rare_freq + value

print("전체 단어 수:", word_cnt)
print("빈도가 {} 이하인 희귀 단어수: {}".format(threshold-1, rare_cnt))
'''
from tensorflow.keras.layers import Embedding, Dense, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
''' 문장 길이 확인 최대 길이 17 평균 길이 9
plt.hist([len(s) for s in X_train], bins=50)
plt.xlabel('Length of Samples')
plt.ylabel('Number of Samples')
plt.show()
'''
max_len = 14
X_train = pad_sequences(X_train, maxlen=max_len)
X_test = pad_sequences(X_test, maxlen=max_len)


model = Sequential()
model.add(Embedding(word_cnt, 100))
model.add(LSTM(128))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])

# model.summary()

# X_train= np.array(X_train)
Y_train= np.array(Y_train)
Y_test= np.array(Y_test)

# X_train = np.asarray(X_train).astype(np.float32)
# Y_train = np.asarray(Y_train).astype(np.float32)

# for i in range(10):
#     print(X_train[i])
#     print(Y_train[i])

history = model.fit(X_train, Y_train, epochs=15, batch_size=60, validation_split=0.2)
# model.save('First_model')
loss_and_metrics = model.evaluate(X_test, Y_test)
print('')
print('loss_and_metrics : ' + str(loss_and_metrics))
