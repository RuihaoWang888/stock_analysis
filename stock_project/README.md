# stock_project/README.md（完整版，包含完整代码逐行讲解 + 全部踩坑记录，直接复制使用）
```markdown
# Baostock A股股票数据爬虫项目
> 项目用途：个人Python学习项目，使用baostock免费金融接口获取A股K线行情，完成数据获取、数据清洗、导出CSV文件、matplotlib绘制股价走势图
> 开发环境：MacOS + VSCode + Python虚拟环境
> 虚拟环境路径：/Users/nancy/code/venv_stock

## 项目功能概述
1. 通过baostock平台接口，获取贵州茅台历史日线K线数据：日期、开盘价、最高价、最低价、收盘价、成交量
2. 分页循环读取接口返回数据，组装成Python列表，转换为Pandas的DataFrame二维表格
3. 将原始英文字段名替换为中文列名，方便阅读与查看
4. 使用os模块自动获取脚本所在目录，动态拼接文件路径，解决不同运行方式下的路径报错
5. 将清洗后的行情数据导出为UTF-8编码的CSV文件，Numbers/Excel均可打开查看
6. 使用matplotlib绘制收盘价折线图，修复Mac系统中文方框乱码问题
7. 处理日期时间类型，优化X轴时间刻度，解决日期标签重叠拥挤问题
8. 规范接口登录与登出流程，养成工程代码好习惯

## 项目目录结构
```
stock_project/
├── fetch_real_data.py   # 主程序：数据拉取、清洗、导出CSV、绘图
├── maotai_stock.csv     # 程序运行后自动生成，存储股票行情数据
└── README.md            # 项目说明文档（本文件）
```

## 前置依赖安装
在虚拟环境终端执行下面命令安装依赖包
```bash
pip install baostock pandas matplotlib
```

## VSCode环境配置
1. 选择解释器：`/Users/nancy/code/venv_stock/bin/python`
2. 两种运行代码的方式
   - 方式1：点击VSCode右上角 ▶ 运行按钮（推荐），直接使用右下角选中的Python环境
   - 方式2：终端手动激活虚拟环境，执行命令：`python fetch_real_data.py`

> ⚠️ 重要区分：
> 在终端手动激活的虚拟环境 ≠ VSCode右上角运行按钮所使用的环境。
> 点击运行按钮执行代码，只会使用右下角选中的Python解释器，这是ModuleNotFoundError最常见的根源。

## 完整源码 fetch_real_data.py
```python
# 导入需要用到的第三方库
import baostock as bs
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # 新增：matplotlib时间坐标轴工具

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

# 创建空列表，用来存放从接口读取的每一行股票数据
data_list = []
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
csv_path = os.path.join(base_dir, "maotai_stock.csv")
# 导出表格为csv文件
df.to_csv(csv_path, index=False)
print(f"文件保存成功，路径：{csv_path}")

# ========== 数据类型转换【重要修复】 ==========
# baostock返回的数据全部是字符串，绘图前必须转换类型
df["收盘"] = pd.to_numeric(df["收盘"])
# 新增：日期字符串转为datetime时间类型，用于优化X轴时间刻度
df["日期"] = pd.to_datetime(df["日期"])

# ========== 绘图部分【Mac中文乱码修复 + X轴日期优化】 ==========
plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

plt.figure(figsize=(14,6))
plt.plot(df["日期"], df["收盘"], label="茅台-收盘价")

# 图表标题、坐标轴标签
plt.title("贵州茅台 收盘价走势图")
plt.xlabel("日期")
plt.ylabel("价格")
plt.legend()

# 核心：设置X轴，每3个月标记一次日期
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 退出baostock登录，关闭连接
bs.logout()
print("程序运行结束，已断开baostock连接")
```

## 代码逐段详细讲解
### 1. 导入库
```python
import baostock as bs
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
```
- `baostock`：国内免费的A股数据接口库，不需要申请密钥，匿名获取行情。`bs`是简写别名。
- `pandas`：表格数据处理库，核心用来做数据整理、类型转换、导出csv。别名`pd`。
- `os`：操作系统内置库，用来获取文件绝对路径，解决跨环境路径问题。
- `matplotlib.pyplot`：绘图库，用来绘制折线图。别名`plt`。
- `matplotlib.dates`：matplotlib专门处理时间坐标轴的模块，用来控制X轴日期刻度。

### 2. 登录baostock平台
```python
lg = bs.login()
print("登录信息：", lg.error_msg)
```
- `bs.login()`：向baostock平台建立会话连接，属于接口层面登录，**不需要账号密码匿名访问**。
- 返回结果存入变量`lg`，`lg.error_msg`是登录返回消息，`success`代表登录成功。

### 3. 查询K线数据（核心接口调用）
```python
rs = bs.query_history_k_data_plus("sh.600519",
    "date,open,"
    "high,low,"
    "close,volume",
    start_date="2024-01-01",
    frequency="D",
    adjustflag = "2")
```
- `bs.query_history_k_data_plus()`：baostock新版历史K线查询函数。
- 参数1 `"sh.600519"`：股票代码。`sh`代表上海证券交易所；`sz`代表深圳交易所；600519=贵州茅台。
- 参数2：需要获取的字段列表
    - date：交易日期
    - open：开盘价
    - high：当日最高价
    - low：当日最低价
    - close：当日收盘价
    - volume：成交量
- `start_date`：数据开始日期，从该日期向后抓取交易日数据。
- `frequency="D"`：K线周期。D=日线，W=周线，M=月线。
- `adjustflag`：复权类型
    - 0：不复权
    - 1：前复权（适合看当前视角的价格）
    - 2：后复权（适合做收益率回测，消除分红拆股影响）
> 返回值`rs`：游标结果集（游标对象），不会一次性返回全部数据，需要循环逐行读取。

### 4. 循环读取分页数据
```python
data_list = []
while rs.error_code =='0' and rs.next():
    data_list.append(rs.get_row_data())
```
- `data_list = []`：初始化空列表，用来存储每一行行情数据。
- `rs.error_code == '0'`：判断接口查询没有报错。
- `rs.next()`：读取下一行数据。读到数据末尾没有更多数据时返回False，循环终止。
- `rs.get_row_data()`：取出当前这一行的数据，返回列表格式，例如`['2024-01-02','1680','1688','1670','1675','23456']`。
- `data_list.append()`：把单行数据追加进列表，收集全部交易日数据。

> 原理：baostock做了分页，一次性不会返回全部数据，必须while循环读取。

### 5. 转为DataFrame表格
```python
df = pd.DataFrame(data_list, columns=rs.fields)
```
- `pd.DataFrame()`：创建Pandas二维表格，类似Excel工作表。
- `data_list`：我们循环收集的全部行数据。
- `columns=rs.fields`：自动从接口结果读取字段名称，作为表格的表头。
- `df`：DataFrame变量，后续所有数据清洗操作都在df上操作。

### 6. 修改列名，英文转中文
```python
df.rename(columns={
    "date": "日期",
    "open": "开盘",
    "high": "最高点",
    "low": "最低点",
    "close": "收盘",
    "volume": "成交量"
}, inplace=True)
```
- `df.rename()`：修改列名。
- `columns={旧名称:新名称}`：字典，批量映射替换表头文字。
- `inplace=True`：直接在原df对象上修改，不生成新的表格副本。

### 7. 动态路径 + 导出CSV文件
```python
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "maotai_stock.csv")
df.to_csv(csv_path, index=False)
print(f"文件保存成功，路径：{csv_path}")
```
- `__file__`：Python内置变量，代表当前`fetch_real_data.py`脚本文件。
- `os.path.abspath(__file__)`：获取脚本完整绝对路径。
- `os.path.dirname()`：提取路径中的文件夹部分，也就是脚本所在目录。
- `os.path.join()`：安全拼接文件夹路径和文件名，自动适配Mac/Windows的路径分隔符。
- `df.to_csv()`：导出表格为csv文件。
- `index=False`：**非常重要**，不导出pandas自动生成的0,1,2...行索引，否则Excel打开会多出一列多余数字。

### 8. 数据类型转换（核心修复）
```python
df["收盘"] = pd.to_numeric(df["收盘"])
df["日期"] = pd.to_datetime(df["日期"])
```
- `pd.to_numeric()`：把收盘列从字符串转为数字类型。baostock返回所有数据默认都是字符串，不转换无法绘图计算。
- `pd.to_datetime()`：把日期字符串转为datetime时间类型，matplotlib才能识别时间，实现智能刻度控制。

### 9. 绘图代码
```python
plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

plt.figure(figsize=(14,6))
plt.plot(df["日期"], df["收盘"], label="茅台-收盘价")

plt.title("贵州茅台 收盘价走势图")
plt.xlabel("日期")
plt.ylabel("价格")
plt.legend()

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```
- `plt.rcParams`：全局绘图参数。`PingFang SC`是Mac自带苹方字体，解决中文方框；`axes.unicode_minus=False`修复负号方框。
- `plt.figure(figsize=(14,6))`：新建画布，宽14英寸，高6英寸。
- `plt.plot(x,y)`：绘制折线图，x=日期，y=收盘价。
- `plt.title()`：图表标题；`plt.xlabel/ylabel`：坐标轴文字；`plt.legend()`：图例。
- `ax = plt.gca()`：获取当前图表坐标轴对象，用来精细控制X轴。
- `mdates.MonthLocator(interval=3)`：设置主刻度，**每3个月显示一次日期标签**，避免标签拥挤。
- `mdates.DateFormatter("%Y-%m")`：日期格式，显示为`2024-01`（年-月）。
- `plt.xticks(rotation=45)`：X轴文字旋转45°，防止文字重叠。
- `plt.tight_layout()`：自动调整图表边距，防止标题、坐标轴文字被截断。
- `plt.show()`：弹出独立窗口展示图表。

### 10. 关闭接口连接
```python
bs.logout()
print("程序运行结束，已断开baostock连接")
```
断开和baostock平台的会话连接，释放资源。属于工程规范，不写代码也可以运行，但正式项目建议保留。

## 项目踩坑全记录 ⭐学习重点
### 坑1：matplotlib中文全部变成方框「□□□」（豆腐块乱码）
- 现象：图表标题、坐标轴、图例中文全部显示方框，无法识别
- 原因：matplotlib默认不加载Mac系统自带中文字体，找不到字体渲染中文
- 解决方案：配置Mac苹方字体
```python
plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False
```

### 坑2：股价曲线是一条斜向上直线，没有真实涨跌波动
- 现象：绘图出来不是正常股价波动曲线，近似一条斜线
- 根本原因：**baostock接口返回的所有数据全部是字符串str类型，不是数字**。matplotlib把价格当成文本绘制，不会识别为数值。
- 解决方案：`pd.to_numeric()`把价格列转为数值
```python
df["收盘"] = pd.to_numeric(df["收盘"])
```

### 坑3：X轴日期密密麻麻堆叠在一起，标签严重重叠
- 现象：X轴每一天的日期全部打印，文字挤成一团，看不清
- 原因：原始日期只是字符串，matplotlib不会识别时间，会把每一行都当成独立文本生成刻度。
- 解决方案：
1. 日期转为datetime时间类型 `df["日期"] = pd.to_datetime(df["日期"])`
2. 使用matplotlib.dates设置按月刻度，间隔3个月生成一个标签
```python
import matplotlib.dates as mdates
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
```

### 坑4：导出CSV文件IO路径报错
- 现象：点击VSCode运行按钮，保存csv时报路径找不到、权限报错
- 原因：直接写相对路径，**不同启动方式（终端/右上角运行）的工作目录不一样**，导致文件保存位置错乱。
- 解决方案：os模块获取脚本绝对路径，动态拼接文件路径
```python
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "maotai_stock.csv")
```

### 坑5：ModuleNotFoundError，找不到baostock/pandas库
- 现象：代码提示`No module named 'baostock'`，但是pip已经安装包
- 原因：VSCode右下角选中的Python解释器，不是安装包的虚拟环境
- 解决方案：手动选择解释器，选中`venv/bin/python`

## 自定义修改示例
1. 更换股票标的：`sh.600036`招商银行 / `sz.000001`平安银行
2. 修改起始时间：`start_date="2020-01-01"`，抓取更长周期行情
3. 切换周线：`frequency="W"`
4. 切换前复权：`adjustflag="1"`

## 学习总结
1. baostock接口返回数据默认全部为字符串，拿到数据后**必须做类型转换**，数值、日期都要单独处理。
2. matplotlib绘制时间序列图表，优先把日期转为datetime类型，使用mdates模块管理坐标轴刻度。
3. Mac平台使用matplotlib绘图，第一件事配置中文字体，避免中文方框乱码。
4. 写文件保存代码，尽量使用`__file__`获取脚本绝对路径，规避不同运行环境的工作目录不一致问题。
5. 游标结果集rs，必须使用while循环+rs.next()逐行读取，这是baostock固定分页读取写法。

## 拓展学习方向
1. 增加5日均线MA5、20日均线MA20计算，叠加绘制在同一张图
2. 新增成交量副图，上下分图，价格在上、成交量在下
3. 将生成的图表自动保存为png图片，不弹出窗口
4. 编写循环，批量下载多只股票行情数据
5. 增加简单策略回测逻辑


### 知识点：函数参数辨析
```python
rs = bs.query_history_k_data_plus("sh.600519",
    "date,open,"
    "high,low,"
    "close,volume",
    start_date="2024-01-01",
    frequency="D",
    adjustflag = "2")
❌ 不是字典！字典使用大括号{}。
✅ 圆括号()内是函数调用的参数列表，分为两类：
位置参数："sh.600519"、字段字符串，只写值，依靠先后顺序匹配函数定义的形参。
Python 语法特性：连续书写的字符串字面量会自动拼接，"a,""b"等价于"a,b"。
关键字参数：start_date="2024-01-01"、frequency="D"、adjustflag="2"，格式参数名=值，可以不严格遵守顺序，必须写在位置参数之后。

bs.query_history_k_data_plus(
    code,                # 参数1：股票代码（位置参数）
    fields,              # 参数2：你想要获取哪些数据【字段列表，逗号分隔字符串】
    start_date=None,
    end_date=None,
    frequency="D",
    adjustflag="0"
)这个是这个代码在baostock上面获取参数的接口

### 知识点：rs.error_code == '0' 详解
```python
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())
rs：调用query_history_k_data_plus返回的baostock 结果集对象，不是 DataFrame。
对象自带属性：
rs.error_code：接口错误码，是字符串类型
rs.error_msg：错误信息文本
rs.error_code == '0'
含义：本次接口查询请求没有报错。
值为字符串'0'：查询成功，正常获取结果集
非'0'（如'1'、'-1'）：查询失败，例如代码写错、字段错误、网络异常、日期非法。
⚠️ 重要：error_code是字符串，必须写'0'带引号，不能直接写数字0。
and rs.next()
and短路逻辑：先判断接口无报错，才尝试读取下一行。一旦接口报错，不再执行 rs.next ()。
rs.next()：去读取下一条行情记录
成功读到一行：返回True，数据存入 rs 内部缓存
读到数据集末尾，没有更多数据：返回False，循环终止。
rs.get_row_data()：取出rs.next()刚刚读到的那一行数据。
区分两个概念
rs.error_code == '0'：检查【接口请求本身是否成功】
rs.next()：检查【是否还有下一行数据可以读取】


//////////////////////////开始用 try... except... finally////////////////////////////////
///////////////////////////////////异常捕获//////////////////////////////////////////////
目标
给咱们的股票脚本加上 try...except 异常捕获。
作用：网络波动、接口报错、字段写错、网络断开的时候程序不会直接崩溃退出，而是打印错误信息，方便排查。
核心思路：
把网络请求、拉取数据这一段放进 try；
except 捕获异常，打印错误；
最后 finally 里面放 bs.logout()，无论成功还是报错，都一定会登出 baostock（很重要，释放会话）。
完整加了异常捕获的代码
python
运行
# 导入库
import baostock as bs
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    # 用来保存结果集，方便finally里面判断
    rs = None
    lg = None
    data_list = []
    try:
        # 登录baostock
        lg = bs.login()
        print(f"登录返回信息：{lg.error_msg}")

        # 调用接口查询K线
        rs = bs.query_history_k_data_plus("sh.600519",
            "date,open,"
            "high,low,"
            "close,volume",
            start_date="2024-01-01",
            frequency="D",
            adjustflag="2")

        # 判断接口查询是否成功
        if rs.error_code != '0':
            raise Exception(f"接口查询失败：{rs.error_msg}")

        # 循环读取每一行数据
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        # 转为DataFrame
        df = pd.DataFrame(data_list, columns=rs.fields)

        # 修改列名英文转中文
        df.rename(columns={
            "date": "日期",
            "open": "开盘",
            "high": "最高点",
            "low": "最低点",
            "close": "收盘",
            "volume": "成交量"
        }, inplace=True)

        # 获取脚本绝对路径，拼接csv保存位置
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "maotai_stock.csv")
        df.to_csv(csv_path, index=False)
        print(f"csv文件保存成功：{csv_path}")

        # 数据类型转换
        df["收盘"] = pd.to_numeric(df["收盘"])
        df["日期"] = pd.to_datetime(df["日期"])

        # 绘图设置
        plt.rcParams["font.family"] = ["PingFang SC"]
        plt.rcParams["axes.unicode_minus"] = False

        plt.figure(figsize=(14, 6))
        plt.plot(df["日期"], df["收盘"], label="茅台-收盘价")
        plt.title("贵州茅台 收盘价走势图")
        plt.xlabel("日期")
        plt.ylabel("价格")
        plt.legend()

        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        # 捕获所有异常，打印错误信息
        print("====程序捕获到异常！====")
        print(f"错误详情：{e}")

    finally:
        # 无论是否报错，都会执行，退出登录
        if lg is not None:
            bs.logout()
            print("已执行登出baostock")

if __name__ == "__main__":
    main()
代码讲解（可以追加进 README）
markdown
### 新增知识点：try ... except ... finally 异常捕获
作用：防止网络中断、参数写错、接口异常时程序直接崩溃，捕获错误并打印提示。
- `try`：放我们正常要执行的业务代码（登录、拉取数据、绘图、导出文件）。
- `except Exception as e`：当try里面任意代码抛出异常，进入这里，打印错误信息。
- `finally`：**无论代码正常跑完，还是发生报错，这一段一定会执行**。
  我们把`bs.logout()`放在finally，保证会话一定会关闭，不会残留连接。

> 额外增加手动抛错：
> ```python
> if rs.error_code != '0':
>     raise Exception(f"接口查询失败：{rs.error_msg}")
> ```
> baostock的error_code不等于0的时候，本身不会自动抛出Python异常，
> 所以我们手动raise，主动触发异常，让except捕获这个接口查询失败的情况。
测试怎么验证异常捕获是否生效？
你可以故意制造错误测试：
股票代码改成不存在的，比如sh.999999，运行，程序不会直接崩溃，会打印接口查询失败
断网运行脚本，会捕获网络相关异常
fields 里面随便写一个不存在字段，比如xxx，会捕获报错
小提醒
我把全部代码封装进main()函数，是 Python 工程推荐写法，后续维护更方便。
if __name__ == "__main__": main() 是固定写法，只有直接运行这个 py 文件才执行 main。

### 知识点：try ... except ... finally 中的 finally
```python
try:
    # 主业务代码：登录、拉取行情、导出CSV、绘图
except Exception as e:
    # 捕获异常，仅代码出错时执行
    print("====程序捕获到异常！====")
    print(f"错误详情：{e}")
finally:
    # ✅【重点】无论try代码正常执行完成，还是中途抛出异常报错，finally内代码一定会执行
    if lg is not None:
        bs.logout()
        print("已执行登出baostock")
使用场景：资源清理。
我们和 baostock 建立网络会话（bs.login()），需要配套bs.logout()释放会话。
哪怕代码中途网络中断、参数错误，程序崩溃，finally 依然会执行登出操作，避免会话残留。
if lg is not None判断：
如果登录环节本身就失败，变量lg没有成功创建，此时不能调用bs.logout()，会引发额外报错。
加判断，保证只有登录成功拿到 lg 对象时，才执行登出。
执行顺序总结：
代码正常运行：try → 跳过except → finally
代码出现异常：try中断 → except捕获打印错误 → finally
规范：finally 里面只放资源释放、清理代码，不要写业务计算、绘图、文件保存这类逻辑。

### 知识点：为什么 "__main__" 需要双引号
```python
if __name__ == "__main__":
    main()
__name__：Python 内置变量，不带引号，变量里面存储的内容是一段字符串文本。
"__main__"：字符串常量。代码中书写文本字符串，必须使用单引号 / 双引号包裹。
== 是相等比较运算符：用来对比左边变量__name__里面的值，是否等于右边的文本__main__。
❌ 错误写法：if __name__ == __main__:
不加引号，Python 会认为__main__是一个变量名称，尝试去寻找这个变量，会触发NameError未定义报错。
简单记忆：
变量名 → 无引号
文字 / 字符串内容 → 必须加引号

### 项目改造总结：模块化封装与异常捕获
本次脚本完成工程化升级：
1. 使用`def main()`把整套业务代码封装为函数，实现模块化。
    优点：代码集中，便于后续修改、新增功能；函数内部变量为局部变量，不污染全局环境。
2. `if __name__ == "__main__": main()`
    - 直接运行当前py文件：执行`main()`；
    - 被其他文件`import`导入：不会自动执行股票查询，需要手动调用`main()`。
3. `try...except...finally`异常捕获
    - try：放置登录、拉取数据、导出csv、绘图等核心业务代码；
    - except：捕获异常并打印错误信息，防止程序直接崩溃；
    - finally：资源清理，**无论正常结束还是报错，都会执行登出bs.logout()**，释放会话连接。

整体代码更健壮，可读性更好，便于后续迭代，也支持被别的项目导入复用


////////////////////////////清洗，去除重复行，处理空值////////////////////////////////
### 知识点：为什么要做数据清洗（去重、空值处理）
从接口抓取得到的原始数据不一定是完美干净的数据，存在脏数据。脏数据会干扰后续数据分析、类型转换、绘图、指标计算，所以需要数据清洗。

1. 去除重复行 drop_duplicates
- 产生原因：网络重试、接口游标异常、多次合并数据，会出现同一交易日多条重复记录。
- 危害：重复数据会导致统计求和、平均值计算结果失真，绘图出现多余线条。
- 处理逻辑：以交易日期`date`作为判断依据，同一天只保留第一条记录，删除重复行。

2. 处理空值 dropna
- 产生原因：服务器数据缺失、股票停牌、网络中断，会出现部分字段为空的残缺行。
- 危害：空值会造成`pd.to_numeric`类型转换异常，绘图线条断裂，均线、涨跌幅等指标计算失效。
- 处理逻辑：只要一行存在空单元格，直接删除该行。股票行情中，价格或成交量为空的记录没有分析价值。

> 清洗时机：拿到原始DataFrame之后，优先清洗，再进行改名、导出、类型转换。尽早清除脏数据，防止脏数据流入后续流程。
补充小思考（方便你理解）
不是所有场景都必须删除空行！
比如人口数据表，年龄为空，我们可以填充平均值；
但是股票行情：价格、成交量是空，代表当天没有有效交易，强行填充数字等于编造虚假行情，所以直接删除更合理。


/////////////////////////优化后的绘图，以及生成img文件的详细解读////////////////////////////////////
整体功能：清洗完成股票数据后，转换数据类型 + 绘制收盘价折线图 + 自动创建 img 目录并保存图片
前置依赖导入（放在 py 文件最顶部）
python
运行
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
① 数据类型转换模块
python
运行
# ========== 数据类型转换【重要修复】 ==========
# baostock返回的数据全部是字符串
df["收盘"] = pd.to_numeric(df["收盘"])
# 新增：日期字符串转为datetime时间类型，用于优化X轴
df["日期"] = pd.to_datetime(df["日期"])
解析
baostock 接口获取的所有原始数据，默认都是字符串 (str) 类型，不能直接做数学计算、绘图时间轴渲染。
pd.to_numeric(df["收盘"])：把「收盘」列从字符串转为数字（float 浮点型），画图、计算均线 / 涨跌幅必须依赖数值类型。
pd.to_datetime(df["日期"])：把日期文本（如2024-09-19）转换成 pandas 时间格式。
作用：matplotlib 可以识别时间，实现按月份控制 X 轴刻度；如果是普通字符串，x 轴会当成普通文本，无法按时间间隔分段。
✅ 重点：这一步是很多新手踩坑点，不做类型转换，后续指标计算、精细日期坐标轴都会异常。
② Matplotlib 全局参数（中文与负号修复）
python
运行
# ========== 绘图部分【Mac中文乱码修复 + X轴日期优化】 ==========
plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False
解析
plt.rcParams["font.family"] = ["PingFang SC"]：设置全局字体为 Mac 自带苹方字体。解决图表里中文变成方框乱码的问题。
Windows 一般用SimHei，Mac 推荐 PingFang SC。
plt.rcParams["axes.unicode_minus"] = False：修复负号显示成方框的 bug（比如下跌涨跌幅的负号）。
③ 自动创建图片保存文件夹
python
运行
# 自动创建img文件夹
base_dir = os.path.dirname(os.path.abspath(__file__))
img_folder = os.path.join(base_dir, "img")
if not os.path.exists(img_folder):
    os.makedirs(img_folder)
解析
os.path.abspath(__file__)：获取当前 python 脚本文件的绝对路径。
os.path.dirname()：拿到脚本所在文件夹目录。
os.path.join(base_dir, "img")：拼接路径，在脚本同级目录下生成img文件夹路径。
if not os.path.exists(img_folder) 判断文件夹是否存在；os.makedirs()不存在则新建文件夹。
好处：不用手动新建 img 文件夹，代码自动处理，项目迁移到别的电脑也能正常运行。
④ 创建画布 + 绘制折线
python
运行
plt.figure(figsize=(14,6))
plt.plot(df["日期"], df["收盘"], label="茅台-收盘价", color="#2E86AB", linewidth=1.2)

# 图表标题、坐标轴标签
plt.title("贵州茅台 收盘价走势图")
plt.xlabel("日期")
plt.ylabel("价格(元)")
plt.legend()
解析
plt.figure(figsize=(14,6))：新建画布，尺寸宽 14 英寸，高 6 英寸，适合展示长周期日线。
plt.plot(x,y,...)：绘制折线图
x 轴：df["日期"]（时间类型）
y 轴：df["收盘"]（价格数值）
label：图例名称，plt.legend() 会读取这个标签，在图上生成图例。
color：线条颜色；linewidth：线条粗细。
plt.title()：图表大标题
plt.xlabel / plt.ylabel：X 轴、Y 轴的文字说明。
plt.legend()：开启图例。
⑤ 核心：X 轴日期刻度精细化控制（这是你这段代码的亮点）
python
运行
# 核心：设置X轴，每3个月标记一次日期
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
解析
ax = plt.gca()：get current axis，拿到当前绘图坐标轴对象，可以做更底层精细控制（普通 plt 简易接口做不到）。
mdates.MonthLocator(interval=3)：主刻度定位器，每隔 3 个月生成一个刻度标记，不会密密麻麻铺满全部日期。
mdates.DateFormatter("%Y-%m")：日期格式化，刻度文字显示为2024-09这种「年 - 月」格式。
如果不使用 mdates，直接绘图，大量日期会挤在一起，文字重叠看不清，是股票绘图的高频坑。
⑥ 美化布局
python
运行
plt.xticks(rotation=45)
plt.grid(alpha=0.3)  # 增加淡淡的网格，看图更方便
plt.tight_layout()
解析
plt.xticks(rotation=45)：x 轴日期文字旋转 45 度，防止文字重叠。
plt.grid(alpha=0.3)：增加背景网格，alpha 代表透明度（0 完全透明，1 不透明），方便对照价格位置。
plt.tight_layout()：自动调整整体布局，防止标题、坐标轴文字被图片边缘截断，导出图片不会缺字。
⑦ 保存图片 + 释放画布资源
python
运行
# 保存图片
img_path = os.path.join(img_folder, "close_line.png")
plt.savefig(img_path, dpi=120)
plt.close()  # 关闭画布，释放内存，多次运行必加

print(f"✅ 图片已保存至：{img_path}")
# plt.show() # 如果本地想弹窗预览图片，就打开这一行；后台批量跑代码时注释掉
解析
plt.savefig()：把画布保存成 png 图片。dpi=120设置图片分辨率，数值越高图片越清晰，文件体积越大。
plt.close()：关闭当前画布，释放内存。
重要：如果后续循环绘制多张图，不加这行，会不断堆积画布，内存占用越来越高。
plt.show()：弹窗弹出图片预览窗口。
本地调试阶段打开；自动化跑脚本、服务器运行时注释掉，否则程序会卡住等待关闭窗口。
可以直接放到 md 文件的「功能总结」
绘图模块功能说明
类型转换：将字符串格式的日期、价格转为时间类型与数值类型，适配绘图与指标计算。
字体配置：解决 Mac 环境 matplotlib 中文乱码、负号方框问题。
目录自动管理：自动创建img文件夹存放图片，无需手动新建。
绘制收盘价折线图，使用matplotlib.dates精细控制 X 轴，每 3 个月展示一个年月刻度，避免日期拥挤重叠。
美化：增加图例、标题、坐标轴标签、浅色网格，旋转日期文字防止重叠。
输出：保存 png 图片，执行画布释放，避免内存泄漏




////





////////////////模块B/////////////////////////////////////////////
README.md 【batch_clean.py 代码详细解析文档】
markdown
# 批量股票CSV合并清洗与绘图脚本 batch_clean.py
## 项目简介
本脚本用于批量读取 test_data 目录下多个股票行情CSV文件，自动校验文件合法性、合并多源行情数据，执行数据清洗，计算5日均线与5日波动率，输出合并清洗后的汇总csv文件，同时绘制收盘价+5日均线趋势图并保存图片。
依赖库：os、pandas、matplotlib
```python
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os：操作系统内置模块，用来处理文件路径、判断文件夹是否存在、遍历文件夹内文件。
import pandas as pd：数据分析核心库，用于读取 csv、表格合并、清洗、指标计算。行业惯例简写为 pd。
import matplotlib.pyplot as plt：绘图库，绘制折线图。简写 plt。
import matplotlib.dates as mdates：matplotlib 专门处理日期坐标轴，用来控制 X 轴日期刻度显示。
python
运行
def main():
定义主函数 main()，所有业务逻辑写在 main 函数内。
规范：把代码封装进函数，避免全局变量污染；后续可以直接导入这个函数复用。
python
运行
    # 1. 获取项目路径，定义各个文件/文件夹位置
    base_dir = os.path.dirname(os.path.abspath(__file__))
__file__：代表当前脚本文件（batch_clean.py）的完整路径。
os.path.abspath(__file__)：拿到脚本绝对完整路径。
os.path.dirname()：取出路径中的文件夹部分（去掉文件名）。
base_dir：项目根目录，后续所有文件都基于这个路径拼接，保证 Mac/Windows 都能正常运行，不会出现相对路径错乱。
python
运行
    test_data_dir = os.path.join(base_dir, "test_data")
os.path.join(a,b)：安全拼接路径，自动适配不同系统的斜杠（Mac 用/，Windows 用\）。
这里拼接出存放原始 csv 数据的文件夹：项目根目录/test_data。
python
运行
    output_csv_path = os.path.join(base_dir, "summary.csv")
定义输出文件路径：项目根目录下的 summary.csv，保存合并清洗完成后的全部数据。
python
运行
    img_folder = os.path.join(base_dir, "img")
定义图片保存文件夹路径：项目根目录 /img，走势图会保存在这里。
python
运行
    df_list = []
创建空列表df_list，用来存放每一个读取成功、校验通过的 DataFrame。后面用 pd.concat 一次性合并全部表格。
python
运行
    try:
开启异常捕获块。try包裹核心业务代码；如果里面任意代码抛出错误，会直接跳到底部except，不会直接粗暴终止程序。
python
运行
        # 判断test_data文件夹是否存在
        if not os.path.exists(test_data_dir):
            raise FileNotFoundError(f"文件夹不存在：{test_data_dir}")
os.path.exists(路径) 判断路径是否存在。
如果 test_data 文件夹不存在，手动抛出FileNotFoundError文件不存在异常。
raise主动抛出异常，交给外层 except 捕获，打印提示。
作用：提前预警，避免后面读取文件时报错。
python
运行
        # 读取test_data目录下全部文件，筛选后缀为csv的文件
        file_names = os.listdir(test_data_dir)
os.listdir(文件夹路径)：列出文件夹里面所有文件和子文件夹名称，返回字符串列表。
python
运行
        csv_file_list = [f for f in file_names if f.lower().endswith(".csv")]
列表推导式，筛选 csv 文件：
f.lower()：把文件名全部转为小写，兼容.CSV大写后缀的文件。
.endswith(".csv")：只保留后缀是 csv 的文件。
作用：过滤掉文件夹、图片、txt 等无关文件，只处理 csv。
python
运行
        print(f"✅ 一共找到 {len(csv_file_list)} 个csv文件，开始读取")
打印找到的 csv 数量，作为日志，方便调试。
python
运行
        # 循环逐个读取每一个csv文件
        for file_name in csv_file_list:
for 循环，遍历每一个筛选出来的 csv 文件名。
python
运行
            file_full_path = os.path.join(test_data_dir, file_name)
拼接单个 csv 文件的完整绝对路径。
python
运行
            print(f"\n正在读取文件：{file_name}")
            try:
                # 优先使用utf-8编码读取csv
                df_temp = pd.read_csv(file_full_path, encoding="utf-8")
            except:
                # utf-8读取失败，自动尝试gbk编码（兼容中文旧文件）
                try:
                    df_temp = pd.read_csv(file_full_path, encoding="gbk")
                except Exception as e:
                    print(f"❌ {file_name} 读取失败，跳过！错误：{e}")
                    continue
嵌套 try-except：
优先 utf-8 读取（现代标准 csv 编码，中文不乱码）。
utf-8 报错（中文乱码 / 编码不匹配），自动尝试 GBK 编码（Windows 旧 Excel 导出文件常用编码）。
如果两种编码都读取失败，打印错误信息，continue直接跳过当前文件，进入下一轮循环，不中断整体程序。
pd.read_csv()：pandas 读取 csv 文件，返回 DataFrame（pandas 的表格对象）。
python
运行
            # 清理列名：去除列名前后多余空格，防止 " 日期 " 和 "日期" 识别成不同列
            df_temp.columns = df_temp.columns.str.strip()
df_temp.columns：获取所有表头列名。
.str.strip()：字符串方法，删除列名首尾的空格、制表符、换行符。
坑点：很多 Excel 导出的 csv 表头会自带空格，肉眼看不见，" 收盘 "和"收盘"会被判定为两个不同列。
python
运行
            print(f"{file_name} 的原始列名：{df_temp.columns.tolist()}")
.tolist()把列名对象转为普通列表，打印出来，方便我们肉眼查看当前文件有哪些字段，调试用。
python
运行
            # 数据校验：必须同时包含【日期】和【收盘】两列，否则判定为无效文件直接跳过
            if "日期" not in df_temp.columns or "收盘" not in df_temp.columns:
                print(f"⚠️ {file_name} 缺少【日期/收盘】列，判定为坏文件，跳过！")
                continue
业务校验逻辑：我们的后续计算必须依赖日期、收盘这两列。如果文件缺少任意一列，这个文件无法参与合并，直接跳过。
continue 跳出本次循环，读取下一个文件。
python
运行
            print(f"✅ {file_name} 通过校验，加入合并列表")
            df_list.append(df_temp)
校验通过，把当前这个表格 df_temp 追加到 df_list 列表，等待后续合并。
python
运行
        # 如果没有任何有效csv，直接退出程序
        if len(df_list) == 0:
            print("⚠ 没有成功读取任何有效的csv文件，程序退出")
            return
循环读完所有 csv 之后，如果 df_list 是空的（所有文件全部损坏 / 校验失败），直接 return 退出 main 函数，不再执行后面的合并、绘图代码。
python
运行
        # 把所有合格的DataFrame合并成一张大表，ignore_index重置行号
        df_all = pd.concat(df_list, ignore_index=True)
pd.concat([df1,df2,df3])：竖向堆叠多个表格，上下拼接。
ignore_index=True：重置行索引。
不写这个参数，每个文件自带的行号会保留，合并后索引重复，后续筛选、索引操作容易出错。
python
运行
        print(f"\n全部有效文件合并完成，合并后总行数：{len(df_all)}")
        df_all.columns = df_all.columns.str.strip()
        print("===合并后全部列名===")
        print(df_all.columns.tolist())
打印合并后的总行数，再次清理合并后的全部列名，输出全部列名用于调试。
python
运行
        # 只保留我们需要的两列：日期、收盘
        need_cols = ["日期", "收盘"]
        df_all = df_all[need_cols]
切片，只保留我们需要的两列，丢弃开盘、最高、最低、成交量等不需要的多余字段，精简数据集。
python
运行
        print("\n===== 开始数据清洗 =====")
        # 按日期去重，保留第一条重复日期的数据
        df_all = df_all.drop_duplicates(subset=["日期"], keep="first")
drop_duplicates：删除重复行
subset=["日期"]：只根据【日期】这一列判断重复。同一个日期出现多条记录，判定重复。
keep="first"：重复多条，保留第一次出现的那一行，后面重复记录直接删除。
场景：多个 csv 文件存在重叠时间段，同一交易日多条数据，会造成均线计算错误。
python
运行
        # 将收盘列转为数值类型，无法转换的脏数据自动变成 NaN
        df_all["收盘"] = pd.to_numeric(df_all["收盘"], errors="coerce")
pd.to_numeric：强制把收盘列转为数字。
errors="coerce"：遇到无法转为数字的脏数据（文字、空字符串、符号），转为NaN（Not a Number，空值标记）。
坑：csv 里收盘字段如果混入文字，会让整列变成字符串类型，rolling 均线计算直接报错。
python
运行
        # 向前填充空值：缺失的收盘价，用上一行有效价格填充
        df_all["收盘"] = df_all["收盘"].ffill()
ffill() = forward fill，向前填充。如果某一行收盘是 NaN，取上一行不为空的收盘价填充。
适合时间序列行情数据，临时缺失价格用上一日价格补齐。
python
运行
        # 删除收盘仍然为空的行，避免后续计算指标时报错
        df_all = df_all.dropna(subset=["收盘"])
dropna删除空值行。subset=["收盘"]：只检查收盘这一列，如果收盘是空，直接删除整行。
ffill 填充后，依然无法补齐的空数据直接丢弃，防止 rolling 计算报错。
python
运行
        print(f"清洗完成，去重后行数：{len(df_all)}")
打印清洗之后剩余有效数据行数。
python
运行
        print("\n===== 计算统计指标列 =====")
        # 5日移动平均线
        df_all["收盘_5日均值"] = df_all["收盘"].rolling(window=5).mean()
rolling(window=5)：滚动窗口，窗口大小 = 5。
mean()：窗口内 5 个数字求平均值，就是 5 日均线。
原理：第 5 行开始才有有效值；前 4 行数据不足 5 个，生成 NaN。
python
运行
        # 5日标准差（波动率）
        df_all["5日波动率"] = df_all["收盘"].rolling(window=5).std()
.std()：计算窗口内标准差，代表价格波动幅度。数值越大，近期股价波动越大。
python
运行
        # 将日期字符串转为datetime时间类型，用于绘图
        df_all["日期"] = pd.to_datetime(df_all["日期"], errors="coerce")
pd.to_datetime：把文本格式的日期字符串（如2024-01-02）转换成 pandas 时间格式。
重要！matplotlib 绘图必须使用时间类型，否则 X 轴不会按时间顺序排列，图表错乱。
errors="coerce"：无法解析的无效日期转为 NaN。
python
运行
        # 按日期从小到大排序
        df_all = df_all.sort_values("日期", ascending=True).reset_index(drop=True)
sort_values：按日期排序。ascending=True升序（从旧到新）。
reset_index(drop=True)：排序完成后重置行索引，丢弃旧索引。
坑：多个文件合并，日期顺序混乱，不排序折线图来回交叉，图表完全失效。
python
运行
        # 输出清洗合并后的csv文件，encoding=utf-8-sig保证Excel打开不乱码
        df_all.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
to_csv：DataFrame 保存为 csv 文件。
index=False：不把 pandas 自带的行号保存到 csv，否则会多出一列无意义序号。
encoding="utf-8-sig"：带 BOM 标记的 utf8 编码，Windows Excel 打开中文不会乱码；Mac 读取也兼容。
python
运行
        print(f"✅ 汇总表已保存：{output_csv_path}")

        print("\n===== 绘制汇总趋势图 =====")
        # 如果img文件夹不存在，自动创建
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
os.makedirs() 创建文件夹。如果 img 文件夹不存在，自动新建。
坑：如果文件夹不存在，直接 savefig 保存图片会直接抛出文件路径不存在异常。
python
运行
        # 设置Mac中文字体，解决中文方框乱码
        plt.rcParams["font.family"] = ["PingFang SC"]
        plt.rcParams["axes.unicode_minus"] = False
matplotlib 全局参数：
PingFang SC：Mac 苹方字体，用来渲染中文。不设置，中文全部变成方框□。
axes.unicode_minus=False：修复负号（负数价格）显示成方框的 bug。
python
运行
        # 创建画布，尺寸14*6英寸
        plt.figure(figsize=(14,6))
新建画布，设置宽 14 英寸，高 6 英寸。
python
运行
        # 绘制原始收盘价曲线
        plt.plot(df_all["日期"], df_all["收盘"], label="汇总-收盘价", color="#C82423", linewidth=1.2)
        # 绘制5日均线
        plt.plot(df_all["日期"], df_all["收盘_5日均值"], label="5日均值", color="#2E86AB", linewidth=1.2)
plt.plot(x,y)绘制折线图：
x 轴：日期；y 轴：价格
label：图例名称
color：十六进制颜色代码
linewidth：线条粗细
python
运行
        # 图表美化
        plt.title("多文件合并 股票收盘价汇总走势图")
        plt.xlabel("日期")
        plt.ylabel("价格(元)")
        plt.legend()
title：图表标题
xlabel /ylabel：坐标轴名称
legend ()：显示图例（右上角的线条说明）
python
运行
        ax = plt.gca()
        # X轴日期，每3个月显示一次刻度
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.gca() get current axis，拿到当前绘图坐标轴对象。
MonthLocator (interval=3)：主刻度间隔 3 个月，避免日期密密麻麻挤在一起。
DateFormatter：格式化日期显示为年-月。
python
运行
        plt.xticks(rotation=45)
x 轴日期文字旋转 45 度，防止文字重叠。
python
运行
        plt.grid(alpha=0.3)
绘制网格线，alpha 透明度 0.3，淡淡的灰色网格，方便看价格。
python
运行
        plt.tight_layout()
自动调整画布布局，防止标题、坐标轴文字被截断。
python
运行
        # 保存图片
        img_save_path = os.path.join(img_folder, "summary_line.png")
        plt.savefig(img_save_path, dpi=120)
        plt.close()
plt.savefig()保存图片。dpi=120，图片清晰度。
plt.close()关闭画布，释放内存。多次循环绘图不关闭会持续占用内存。
python
运行
        print(f"✅ 图片已保存至：{img_save_path}")

        print("\n🎉 全部任务执行完毕！")

    # 全局异常捕获，程序报错不会直接崩溃，打印错误信息
    except Exception as e:
        print(f"\n===捕获异常，程序中断===")
        print(f"错误信息：{e}")
外层全局 except，捕获 try 块内任意代码抛出的异常。打印错误信息，方便定位问题。
python
运行
if __name__ == "__main__":
    main()
Python 标准入口：只有直接运行本文件时，才执行 main () 函数；如果其他脚本 import 导入这个文件，不会自动执行 main。
markdown
## 整体执行流程总结
1. 初始化项目路径，定义输出文件位置
2. 扫描test_data文件夹，筛选全部csv文件
3. 循环读取每一个csv，自动尝试utf8/gbk编码，读取失败直接跳过
4. 清洗列名空格，校验是否包含【日期、收盘】必要字段
5. 有效表格存入列表，全部读完后合并为一张大表
6. 精简字段，只保留日期、收盘
7. 数据清洗：按日期去重、收盘转为数值、填充空值、删除残留空行
8. 计算指标：5日均线、5日波动率
9. 日期转为时间格式，按时间升序排序
10. 输出summary.csv合并数据表
11. 创建img文件夹，设置中文字体，绘制收盘价+5日均线图
12. 保存图片，输出完成提示