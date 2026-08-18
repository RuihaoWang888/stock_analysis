import yfinance as yf
import pandas as pd
import matplotlib as plt
import time

stock_apple = yf.Ticker("AAPL")

try:
    df = stock_apple.history(period = "30d")
    print(df)
except Exception as err:
    print("被限流了,等30秒")
    time.sleep(30)
    df = stock_apple.history(period = "30d")

print(df.head())

#绘制走势收盘的图
#设置画布的大小
plt.figure(figsize=(10, 5))
#画df的（“close”）
plt.plot(df["close"])
#写标题
plt.title("AAPL 收盘价")
#绘制图，看
plt.show()

#容易限流
