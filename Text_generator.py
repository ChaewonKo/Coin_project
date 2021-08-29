import requests, re, json, yaml
from bs4 import BeautifulSoup 
from konlpy.tag import Okt
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pyupbit


# google sheet setup
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
        r'Datas\cryptocurrency-trading-322311-49fb93070f6f.json', scope)
gs_auth = gspread.authorize(credentials)
# get_gsdata = gs_auth.open_by_url('https://docs.google.com/spreadsheets/d/1Mo2G47zSTdfyeGC8F8SrE8Le_2hQp86xh0zmqYC6aFU/edit#gid=846263781')
# gs_datas = get_gsdata.worksheet('Back data')
BTC_price = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=365)
print(type(BTC_price))
# gs_datas.update_cell(1, 3, 'testing1')

# Okt
# okt = Okt()

# URL = "https://search.naver.com/search.naver?&where=news&query=%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=0&ds=&de=&docid=&nso=so:r,p:all,a:all&mynews=0&cluster_rank=23&start="
# Max_pages = 500
# All_text_list = []

# for i in range(Max_pages):
#     print('{}번째 페이지 데이터 모으는 중'.format(i))
#     req = requests.get(URL+str(i))
#     soup = BeautifulSoup(req.text, 'lxml')

#     titles = soup.select("a.news_tit")

#     for title in titles:
#         title_data = title.text
#         title_data = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…\"\“》]', '', title_data)
#         nmled_data = okt.normalize(title_data)
#         for Noun in okt.nouns(nmled_data):
#             if Noun in All_text_list:
#                 continue
#             else:
#                 All_text_list.append(Noun)


# with open('all_text_2.txt','w') as f:
#     f.write(' '.join( str(e) for e in All_text_list))
# f.close()


