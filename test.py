# import pandas.plotting._matplotlib
# import matplotlib.pyplot as plt
# # plt.rcParams["axes.grid"] = True
# plt.rcParams["figure.figsize"] = (12,6)
# plt.rcParams["axes.formatter.limits"] = -10000, 10000

import pyupbit

# df = pyupbit.get_ohlcv("KRW-BTC")
# print(df)

# # 가격 차트 그리기
# df = pyupbit.get_ohlcv("KRW-BTC", interval='day', count=100)
# # print("\n---BTC 가격---")
# # print(df)
# # df.head(10)

# df[["close"]].plot(secondary_y=["volume"])
# # df["close"].plot()
# plt.show()

import datetime
import matplotlib.pyplot as plt
import mpl_finance
import matplotlib.ticker as ticker

start = datetime.datetime(2016, 3, 1)
end = datetime.datetime(2016, 3, 31)


fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
df = pyupbit.get_ohlcv("KRW-BTC", interval='day', count=100)

mpl_finance.candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.5, colorup='r', colordown='b')
plt.grid()
plt.show()