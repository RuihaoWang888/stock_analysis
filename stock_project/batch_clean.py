import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(base_dir, "test_data")
    output_csv_path = os.path.join(base_dir, "summary.csv")
    img_folder = os.path.join(base_dir, "img")

    df_list = []
    try:
        if not os.path.exists(test_data_dir):
            raise FileNotFoundError(f"文件夹不存在：{test_data_dir}")

        file_names = os.listdir(test_data_dir)
        csv_file_list = [f for f in file_names if f.lower().endswith(".csv")]
        print(f"✅ 一共找到 {len(csv_file_list)} 个csv文件，开始读取")

        for file_name in csv_file_list:
            file_full_path = os.path.join(test_data_dir, file_name)
            print(f"\n正在读取文件：{file_name}")
            try:
                df_temp = pd.read_csv(file_full_path, encoding="utf-8")
            except:
                try:
                    df_temp = pd.read_csv(file_full_path, encoding="gbk")
                except Exception as e:
                    print(f"❌ {file_name} 读取失败，跳过！错误：{e}")
                    continue

            df_temp.columns = df_temp.columns.str.strip()
            print(f"{file_name} 的原始列名：{df_temp.columns.tolist()}")

            if "日期" not in df_temp.columns or "收盘" not in df_temp.columns:
                print(f"⚠️ {file_name} 缺少【日期/收盘】列，判定为坏文件，跳过！")
                continue

            print(f"✅ {file_name} 通过校验，加入合并列表")
            df_list.append(df_temp)

        if len(df_list) == 0:
            print("⚠ 没有成功读取任何有效的csv文件，程序退出")
            return

        df_all = pd.concat(df_list, ignore_index=True)
        print(f"\n全部有效文件合并完成，合并后总行数：{len(df_all)}")
        df_all.columns = df_all.columns.str.strip()
        print("===合并后全部列名===")
        print(df_all.columns.tolist())

        need_cols = ["日期", "收盘"]
        df_all = df_all[need_cols]

        print("\n===== 开始数据清洗 =====")
        df_all = df_all.drop_duplicates(subset=["日期"], keep="first")
        df_all["收盘"] = pd.to_numeric(df_all["收盘"], errors="coerce")
        df_all["收盘"] = df_all["收盘"].ffill()
        df_all = df_all.dropna(subset=["收盘"])
        print(f"清洗完成，去重后行数：{len(df_all)}")

        print("\n===== 计算统计指标列 =====")
        df_all["收盘_5日均值"] = df_all["收盘"].rolling(window=5).mean()
        df_all["5日波动率"] = df_all["收盘"].rolling(window=5).std()

        df_all["日期"] = pd.to_datetime(df_all["日期"], errors="coerce")
        df_all = df_all.sort_values("日期", ascending=True).reset_index(drop=True)

        df_all.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
        print(f"✅ 汇总表已保存：{output_csv_path}")

        print("\n===== 绘制汇总趋势图 =====")
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)

        plt.rcParams["font.family"] = ["PingFang SC"]
        plt.rcParams["axes.unicode_minus"] = False

        plt.figure(figsize=(14,6))
        plt.plot(df_all["日期"], df_all["收盘"], label="汇总-收盘价", color="#C82423", linewidth=1.2)
        plt.plot(df_all["日期"], df_all["收盘_5日均值"], label="5日均值", color="#2E86AB", linewidth=1.2)

        plt.title("多文件合并 股票收盘价汇总走势图")
        plt.xlabel("日期")
        plt.ylabel("价格(元)")
        plt.legend()
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        img_save_path = os.path.join(img_folder, "summary_line.png")
        plt.savefig(img_save_path, dpi=120)
        plt.close()
        print(f"✅ 图片已保存至：{img_save_path}")

        print("\n🎉 全部任务执行完毕！")

    except Exception as e:
        print(f"\n===捕获异常，程序中断===")
        print(f"错误信息：{e}")

if __name__ == "__main__":
    main()