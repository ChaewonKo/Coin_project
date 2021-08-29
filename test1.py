import time
import requests, re, json, yaml
from bs4 import BeautifulSoup 
from konlpy.tag import Okt


URL = "https://kr.coinness.com/"
Max_pages = 500
All_text_list = []
okt = Okt()

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')
# items = soup.select("#index > div.nno > div.fl > div > div.home-container > div:nth-of-type(2) > div.content-wrap > ul")
# for index in range(1, len(items[0])):
#     print(items[0].select("li:nth-of-type({}) > div > div.news-content > div.h63".format(index)))
items = soup.select("#index > div.nno > div.fl > div > div.home-container > div:nth-of-type(3) > div.content-wrap > ul > li")
for item in items:
    data = item.select_one("div > div.news-content > div.h63").get_text()
    print("Data : {}".format(data))
    # print("Score : {}".format(.score(data)))
    print('====================================')

# print(soup.body.div.h63.get_text())
# print(list(soup.children)[2])

#     titles = soup.select("div.h63")

#     for title in titles:
#         title_data = title.text
        # title_data = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…\"\“》]', '', title_data)
        # nmled_data = okt.normalize(title_data)
        # for Noun in okt.nouns(nmled_data):
        #     if Noun in All_text_list:
        #         continue
        #     else:
        #         All_text_list.append(Noun)

# from oauth2client.service_account import ServiceAccountCredentials
# import gspread

# scope = ['https://spreadsheets.google.com/feeds',
#          'https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#         r'cryptocurrency-trading-322311-49fb93070f6f.json', scope)
# gc = gspread.authorize(credentials)

# gc1 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Mo2G47zSTdfyeGC8F8SrE8Le_2hQp86xh0zmqYC6aFU/edit#gid=846263781')
# worksheet = gc1.get_worksheet(0)
# worksheet.update_cell(1, 1,'chaewon_updated1')
# gc2 = gc1.worksheet('정보')
# gc3 = gc2.get_all_values()
# print(gc3)