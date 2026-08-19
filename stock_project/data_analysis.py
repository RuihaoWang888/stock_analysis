import pandas as pd
import matplotlib.pyplot as plt

#读取csv文件
df = pd.read_csv("stock_data.csv")

print("-----打印前5行-----")
print(df.head())

print("-----打印后5行-----")
print(df.tail())

print("-----数据表信息-----")
print(df.info())

print("-----收盘价统计结果-----")
print(df["收盘"].describe())

#新增5日均线列
df["5日均线"] = df["收盘"].rolling(window= 5).mean()

#打印包含均线的后10列
print("均线后面后十列")
print(df.tail(10))

#保存
df.to_csv("stock_data_ma5.csv", index=False)

plt.figure(figsize=(12, 6))
plt.plot(df["日期"], df["收盘"], label = "收盘价", color ="#2E86AB")

plt.plot(df["日期"], df["5日均线"], label = "5日均线", color ="#A23B72")

plt.title("token")
plt.xlabel("日期")
plt.ylabel("价格")
plt.legend()
plt.show()