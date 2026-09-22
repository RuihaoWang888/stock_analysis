import pandas as pd
import matplotlib.pyplot as plt

#读取真实数据表格
df = pd.read_csv("maotai_stock.csv", )

#检查读取是否成功打印前5行数据
print("打印前5行数据")
print(df.head())

#将日期这一列字符串变为，真正的日期
df["日期"] = pd.to_datetime(df["日期"])

df["5日均线"] = 