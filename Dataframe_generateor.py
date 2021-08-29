'''
# BTC 저장
import pyupbit
import pandas as pd
data = pyupbit.get_ohlcv("KRW-BTC", count=365)

up_down = data['close'] - data['open']
up_down_2 = up_down.apply(lambda x: 1 if x > 0 else -1)
up_down_2.dropna(how='any')
up_down_2.to_csv('BTC.csv')
'''
'''
# 시간 데이터 제거
import pandas as pd
price_data = pd.read_csv('Datas/BTC.csv')
# print(price_data)

for index, data in enumerate(price_data['date']):
    price_data['date'][index] = data[:10]
# print(price_data)
price_data.to_csv('BTC_without_time.csv', index=False)
'''

from datetime import datetime, timedelta, date
import pandas as pd
from bs4 import BeautifulSoup 
import requests, re

price_data = pd.read_csv('Datas/BTC_without_time.csv')


price_data2 = price_data.set_index('date').to_dict()

URL = "https://kr.coinness.com/news/"
max_num = 1004924
last_num = 1000106

date_range = 365

last_date = date(2021, 8, 15)
start_date = last_date - timedelta(date_range)
will_save_df = pd.DataFrame(columns=['Text', 'Price'])

def convert_date_format(date):
    date = re.sub('[^0-9]', '', date)
    date = '{}-{}-{}'.format(date[:4], date[4:6], int(date[6:])+1)
    return date

num = 0
while max_num >= last_num + num :
    print('Current Num : {}'.format(num))
    print('Left num : {}'.format(max_num - last_num - num))
    response = requests.get(URL+str(last_num+num))
    soup = BeautifulSoup(response.text, 'html.parser')
    article_title = soup.select_one('title').get_text()
    if ' | 코인니스' in article_title:
        article_title = article_title.replace(' | 코인니스', '')
    elif ' | CoinNess' in article_title:
        article_title = article_title.replace(' | CoinNess', '')
    article_title = re.compile('[가-힣]+').findall(article_title)
    # print(article_title)
    article_date = soup.select_one('#detail > div > div.fl > div > section > div > div.time > span.month').get_text()
    article_date_2 = convert_date_format(article_date)
    num += 2
    if article_date_2 not in price_data2['price']:
        print(article_date_2, 'Error')
        continue
    
    if article_title:
        article_title = ' '.join(article_title)
        # print(article_title)
        will_save_df = will_save_df.append(
            pd.DataFrame( 
                [[article_title, price_data2['price'][article_date_2]]], 
                columns=['Text', 'Price']
                ))

    

will_save_df.to_csv('BTC_dataset_1.csv', index=False)



# print(price_data2['price']['2020-08-16'])
# print('2020-08-16')
# print(last_date)
# print(article_date)
# print(article_title)

 
