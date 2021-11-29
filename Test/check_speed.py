# 업비트 홈페이지와 api의 속도 측정을 위한 스크립트

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import datetime, requests, pyupbit

class SpeedTest():
    def __init__(self):
        s=Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)/AppleWebKit/537.36 \
        #     (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36")
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(service=s, options=options)

        self.URL = "https://api.upbit.com/v1/ticker"
        self.querystring = {"markets":" KRW-STPT"}
        self.headers = {"Accept": "application/json"}




    def main(self):
        while True:
            now = datetime.datetime.now()

            ticker_price_on_web=self.driver.find_element(By.XPATH, '//*[@id="UpbitLayout"]/div[3]/div/section[1]/article[1]/div/span[1]/div[1]/span[1]/strong').text
            # ticker_price_on_backend = requests.request("GET", self.URL, headers=self.headers, params=self.querystring)
            ticker_price_on_backend = pyupbit.get_current_price("KRW-STPT")
            if ticker_price_on_backend:
                # ticker_price_on_backend = ticker_price_on_backend.json()[0]['trade_price']
            
                print('Now : {}, Web : {}, Back : {}'.format(now, ticker_price_on_web, ticker_price_on_backend))


if __name__=='__main__':
    ST = SpeedTest()
    ST.main()
