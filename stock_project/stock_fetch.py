import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

date_range = pd.date_range(start="2024-01-01", periods= 300, freq= "D")

#生成模拟收盘价，从160开始上下浮动
np.random.seed(10)
price = 160 + np.cumsum(np.random.randn(300)*2)


df = pd.DataFrame({
    "日期" : date_range,
    "开盘" : price + np.random.randn(300),
    "最高" : price + abs(np.random.randn(300)),
    "最低" : price - abs(np.random.randn(300)),
    "收盘" : price,
    "成交量" : np.random.randint(20000, 80000, size=300)
})

print(df.head())
print(df.info())

df.to_csv("stock_data.csv", index=False)

plt.figure(figsize=(10,5))
plt.plot(df["日期"],df["收盘"])
plt.title("模拟股票走势-venv stock")
plt.show()
