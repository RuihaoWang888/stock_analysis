import baostock as bs
import pandas as pd

#登录baostock
lg = bs.login()
#检查是否登录成功
print("登录信息: ", lg.error_msg)

#创建结果集result set 缩写rs
rs = bs.query_history_k_data_plus("sh.600519",
                                  "date, open,"
                                  "high, low,"
                                  "close, volume",
                                    start_date="2024-01-01",
                                    frequency= "D", 
                                    adjustflag = "2")

#设置一个数据列表用于存储遍历bs拉取的数据
data_list = []
#while循环
while rs.error_code =='0' and rs.next():
    data_list.append(rs.get_row_data())

#将获取的数据列表放入pandas里面的表格里用DataFrame里面,用inplace=false让表格不重新开一个新的表格写
df = pd.DataFrame(data_list, columns=rs.fields)

#改名，改成中文名方便阅读
df.rename(columns={"date": "日期",
                   "open": "开盘",
                   "high": "最高点",
                   "low": "最低点",
                   "close": "收盘",
                   "volume": "成交量"
}, inplace=True)

df.to_csv("maotai_stock.csv", index=False)

print("打印前5行")
print(df.head())
#退出登录
bs.logout()
