import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#制造模拟日期
dates = pd.date_range(start= "2026-7-1", periods=30)
#生成模拟收盘价
np.random.seed(10)
price = 220 + np.cumsum(np.random.randn(30))

df = pd.DataFrame({
    "date": dates,
    "close": price
})
df = df.set_index("date")

print(df.head())

#画图
plt.figure(figsize=(10, 4))
plt.plot(df["close"])
plt.title("模拟股票走势")
plt.show()
