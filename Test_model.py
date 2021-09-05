from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

max_len = 14

def sentimen_predict(new_sentence):
    new_token = [word for word in Okt.morphs(new_sentence) if not word in stopwords]
    new_sentence = Tokenizer.texts_to_sequences([new_token])
    new_pad = pad_sequences(new_sentence, maxlen=max_len)

    score = float(model.predict(new_pad))