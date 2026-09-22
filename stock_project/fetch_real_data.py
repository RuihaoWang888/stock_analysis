import baostock as bs
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # 新增：时间坐标轴工具

#创建一个函数def 名叫main（）的函数，把代码里面的局部变量全部封装到一个盒子里面，当其他程序调用的时候不会直接运行全部代码
def main():
    # 用来保存结果集，在finally里面运用
    rs = None
    lg = None
    # 创建空列表，用来存放从接口读取的每一行股票数据
    data_list = []

    try:
        # 登录baostock数据平台
        lg = bs.login()
        # 打印登录返回信息，查看是否登录成功
        print("登录信息：", lg.error_msg)

        # 调用接口查询历史K线数据
        rs = bs.query_history_k_data_plus("sh.600519",
            "date,open,"
            "high,low,"
            "close,volume",
            start_date="2024-01-01",
            frequency="D",
            adjustflag = "2")

        if rs.error_code != '0':
            raise Exception(f"接口查询失败，{rs.error_msg}")
        # 循环读取所有K线数据
        while rs.error_code =='0' and rs.next():
            data_list.append(rs.get_row_data())

        # 将列表数据转换成pandas表格DataFrame
        df = pd.DataFrame(data_list, columns=rs.fields)

        # 修改表头，英文列名替换成中文，方便阅读
        df.rename(columns={
            "date": "日期",
            "open": "开盘",
            "high": "最高点",
            "low": "最低点",
            "close": "收盘",
            "volume": "成交量"
        }, inplace=True)

        # 获取当前脚本文件所在的文件夹路径，解决相对路径保存文件报错
        base_dir = os.path.dirname(os.path.abspath(__file__))
        raw_path = os.path.join(base_dir, "maotai_stock_清洗前数据.csv")
        # 导出表格为csv文件
        df.to_csv(raw_path, index=False)
        #计数有多少行数据
        raw_row_count = len(df)
        print(f"清洗前数据已保存:{raw_path}, 一共{raw_row_count}行")
        

        #开始清洗，处理重复行，处理空值
        #按日期开始去重，同一天记录只留第一条
        df = df.drop_duplicates(subset = ["日期"], keep = "first")
        #删除存在空值的行，如果要删除其中一个列的行，比如[收盘]，就用df = df.dropna(subset= ["收盘"])
        df = df.dropna()
        #======== 新增：按交易日期生序，重置索引=========
        df = df.sort_values("日期", ascending=True).reset_index(drop=True)
        print("✅ 数据已按交易日期生序排序，索引重置完成")
        #计数现在干净的数据有多少行
        clean_row_count = len(df)
        #计算一共清理了多少行数据
        delete_row_count = raw_row_count - clean_row_count
        print(f"干净的数据一共有{clean_row_count}行")
        print(f"原始的数据一共{raw_row_count}行，肮脏的数据一共{delete_row_count}行")
        #导出清理过后的csv文件
        clean_path = os.path.join(base_dir, "maotai_stock_清洗后数据.csv")
        df.to_csv(clean_path, index=False)
        print(f"清理后的scv文件已保存:{clean_path}")

        #========新增：读取下载好的csv，用df.head(),df.describe()查看数据 ==============
        df_check = pd.read_csv(clean_path)
        print("\n======数据预览 df.head() =====")
        print(df_check.head())
        print("\n======数据统计描述 df.describe() =====")
        print(df_check.describe())

        # ========== 数据类型转换【重要修复】 ==========
        # baostock返回的数据全部是字符串
        df["收盘"] = pd.to_numeric(df["收盘"])
        # 新增：日期字符串转为datetime时间类型，用于优化X轴
        df["日期"] = pd.to_datetime(df["日期"])

        # ========== 绘图部分【Mac中文乱码修复 + X轴日期优化】 ==========
        plt.rcParams["font.family"] = ["PingFang SC"]
        plt.rcParams["axes.unicode_minus"] = False

        # 自动创建img文件夹
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_folder = os.path.join(base_dir, "img")
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)

        plt.figure(figsize=(14,6))
        plt.plot(df["日期"], df["收盘"], label="茅台-收盘价", color="#2E86AB", linewidth=1.2)

        # 图表标题、坐标轴标签
        plt.title("贵州茅台 收盘价走势图")
        plt.xlabel("日期")
        plt.ylabel("价格(元)")
        plt.legend()

        # 核心：设置X轴，每3个月标记一次日期
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)  # 增加淡淡的网格，看图更方便
        plt.tight_layout()

        # 保存图片
        img_path = os.path.join(img_folder, "close_line.png")
        plt.savefig(img_path, dpi=120)
        plt.close()  # 关闭画布，释放内存，多次运行必加

        print(f"✅图片已保存至：{img_path}")
        # plt.show() # 如果本地想弹窗预览图片，就打开这一行；后台批量跑代码时注释掉

    except Exception as e:
        #捕获所有异常，打印错误信息
        print(f"===程序捕获到异常===")
        print(f"错误详情：{e}")

    finally:
        #无论是否有异常或报错，都会执行，退错登录
        if lg is not None:
            bs.logout()
            print("程序运行结束，已断开baostock链接")

if __name__ == "__main__":
    main()