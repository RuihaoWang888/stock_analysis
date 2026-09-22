# python_error.md 踩坑记录
## 坑1：baostock返回全部数据是字符串类型
问题：直接绘图、计算指标会报错，无法做数值运算
解决：pd.to_numeric()转换价格；pd.to_datetime()转换日期

## 坑2：Excel打开csv，日期列显示#####
原因：单元格宽度不足，不是数据损坏
解决：Excel双击列分隔线，自动适配列宽

## 坑3：matplotlib中文方框乱码
原因：缺少中文字体配置
解决：plt.rcParams["font.family"] = ["PingFang SC"]；关闭负号unicode_minus

## 坑4：X轴日期标签全部挤在一起重叠
解决：使用matplotlib.dates.MonthLocator，按月份控制刻度

## 坑5：多次绘图不关闭画布，内存持续上涨
解决：plt.close()保存图片之后关闭画布释放内存


////////rm -r ..../////////
rm: batch_clean.py: is a directory
意思：batch_clean.py 现在不是文件，而是一个文件夹！
你之前不小心创建了名字叫 batch_clean.py 的目录，rm 命令默认不能直接删文件夹，所以报错。
解决命令（Mac 终端）
删除这个名叫 batch_clean.py 的文件夹（里面如果有内容会全部删掉）
bash
rm -r batch_clean.py
-r = recursive，递归删除目录，加 -i 就是交互式确认：rm -ri batch_clean.py
删完之后，再新建真正的 batch_clean.py 文件（普通文件，不是文件夹）
bash
touch batch_clean.py
验证是否正常
执行 ls 看目录列表：
bash
ls
现在 batch_clean.py 应该是 - 开头（普通文件），而不是 d 开头（directory 文件夹）。
为什么会出现这个问题：大概率是你之前执行 mkdir batch_clean.py 了，mkdir 会创建文件夹，千万不要用 mkdir 创建 py 脚本。
✅ 创建 python 脚本：touch batch_clean.py
❌ 不要：mkdir batch_clean.py
执行完删除命令后，就可以把模块 B 代码粘贴进 batch_clean.py 文件里，正常运行。




python_error.md 【完整踩坑记录，超详细版】
markdown
# batch_clean.py 项目踩坑与错误记录
> 记录开发过程中遇到的所有报错、现象、原始报错文本、排查思路、根因分析、修复代码、验证方法
## 错误1：文件后缀名是 .csv，但文件本体是xlsx二进制文件（本次最核心大坑）
### 现象
- 肉眼看文件名：stock1.csv
- pd.read_csv 没有直接抛出IO读取报错，但是读取后的列名完全乱码，打印列名得到 `['PK\x03\x04', nan]`
- 合并后数据行数极少，清洗之后只剩很少行，执行rolling计算时抛出报错：
> `No numeric types to aggregate`
翻译：没有数值类型可以聚合计算。
### 排查过程
1. 一开始怀疑代码逻辑问题，打印df.columns看到PK开头乱码，很奇怪。
2. 搜索PK\x03\x04：这是zip压缩包文件头部标记。
3. 恍然大悟：xlsx本质是zip压缩二进制文件！
4. 问题来源：Numbers/Excel另存为的时候，保存类型选了xlsx，之后手动把文件名后缀`.xlsx`改成`.csv`。
仅仅修改文件名后缀，**不会修改文件内部二进制结构**。文件里面仍然是xlsx压缩包，不是纯文本CSV。
pd.read_csv只是按文本模式强行读取二进制字节，读到压缩包头部标记，解析成乱码表头。

### 根因
文件扩展名只是名字，**不能改变文件内部数据格式**。
CSV是纯文本，xlsx是二进制压缩包，二者底层完全不同。

### 修复方案
1. 在Numbers/Excel另存为时，文件类型下拉框**直接选择 CSV(逗号分隔)(*.csv)**
2. 编码选项必须选择 UTF-8
3. 文件名完整写 stock1.csv，不要只写stock1
### 验证方法
右键csv文件 → 打开方式 → 文本编辑。打开之后能看到纯文本，逗号分隔数据，没有乱码，才算正常CSV。

## 错误2：列名首尾自带空格，字段匹配判断失效
### 现象
csv表头肉眼看是`日期`，但是代码判断 `"日期" in df.columns` 返回False，程序判定文件缺少列，直接跳过这个正常文件。
打印列名输出：`[' 日期 ', ' 收盘 ']`，列名左右两边藏有空格，肉眼不可见。
### 报错信息
无直接报错，是**逻辑静默错误**（程序不崩溃，但是结果不符合预期，文件被错误跳过，很难排查）
### 根因
Excel/Numbers导出csv时，表头单元格前后空格会一并写入csv表头。字符串比较严格匹配，`"日期"`和`" 日期 "`是两个不同字符串。

### 修复代码
```python
df_temp.columns = df_temp.columns.str.strip()
验证
打印列名，确认空格全部清除。
错误 3：matplotlib 绘图中文变成方框（豆腐块），负号也异常
现象
图片里所有中文标题、坐标轴文字全部变成方框□，数字负号也变成方框。程序无报错，图片正常生成，只是中文无法渲染。
根因
matplotlib 默认不自带中文字体，找不到中文渲染字体，中文字符无法绘制。
修复代码
python
运行
plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False
PingFang SC 是 Mac 系统自带苹方字体；Windows 需要换成 SimHei。
错误 4：多文件合并，同一交易日有多条重复数据，均线计算异常
现象
合并之后，同一个日期出现多条行情记录。绘制图表时，同一个 X 日期有多个 Y 值，均线扭曲失真。无程序报错，属于数据逻辑错误。
根因
多个原始 csv 数据时间段重叠，导出的行情存在重复交易日。
修复代码
python
运行
df_all = df_all.drop_duplicates(subset=["日期"], keep="first")
验证
打印去重前后行数对比，行数减少代表重复数据被删除。
错误 5：收盘价存在空值 NaN，rolling 窗口计算报错
现象
原始 csv 收盘列存在空单元格，在执行 rolling.mean () 的时候抛出异常：No numeric types to aggregate
根因
空值存在，pandas 无法对包含 NaN 的序列做聚合计算。同时，如果收盘列里面混入文字，整列会变成字符串类型，直接无法计算。
分步修复代码
python
运行
# 转为数值，脏数据转为NaN
df_all["收盘"] = pd.to_numeric(df_all["收盘"], errors="coerce")
# 向前填充缺失值
df_all["收盘"] = df_all["收盘"].ffill()
# 删除仍然为空的行
df_all = df_all.dropna(subset=["收盘"])
错误 6：CSV 编码不匹配，读取 csv 直接抛出编码报错
现象
报错原文：UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd5 in position 10: invalid continuation byte
根因
部分 csv 是 GBK 编码（Windows Excel 导出旧文件），直接用 utf-8 读取，字节解码失败。
修复代码（嵌套 try-except 自动切换编码）
python
运行
try:
    df_temp = pd.read_csv(file_full_path, encoding="utf-8")
except:
    try:
        df_temp = pd.read_csv(file_full_path, encoding="gbk")
    except Exception as e:
        print(f"❌ {file_name} 读取失败，跳过！错误：{e}")
        continue
错误 7：img 文件夹不存在，plt.savefig 保存图片时报路径不存在
现象
报错原文：FileNotFoundError: [Errno 2] No such file or directory: 'xxx/img/summary_line.png'
根因
项目目录没有手动新建 img 文件夹，直接保存图片，目标路径不存在。
修复代码
python
运行
if not os.path.exists(img_folder):
    os.makedirs(img_folder)
错误 8：缺少全局异常捕获，单个文件损坏直接导致整个脚本终止
现象
文件夹里其中一个 csv 文件损坏，程序直接崩溃终止，后面剩余 csv 文件不再处理。
根因
没有顶层 try-except 捕获异常，遇到异常直接退出。
修复
增加外层 try...except Exception 捕获全局异常，打印错误信息，优雅退出。
错误 9：合并后日期乱序，绘制折线图线条来回交叉，图表完全错乱
现象
图上折线来回折返，不是按时间从左向右递增。程序无报错，图片生成但是图表无效。
根因
多个 csv 文件读取顺序不确定，合并之后行顺序混乱，日期无序。matplotlib 直接按行顺序绘制，不是自动按 X 轴时间排序。
修复代码
python
运行
df_all["日期"] = pd.to_datetime(df_all["日期"], errors="coerce")
df_all = df_all.sort_values("日期", ascending=True).reset_index(drop=True)
额外小坑：to_csv 保存文件，Excel 打开中文乱码
现象
生成 summary.csv，Mac 打开正常，Windows Excel 打开中文乱码。
根因
默认 utf-8 不带 BOM 标记，Windows Excel 解析 utf8 文件识别异常。
修复：encoding="utf-8-sig"
python
运行
df_all.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
整体排坑总结
CSV 文件不能只改后缀名，导出的时候必须直接选择 CSV 格式，UTF-8 编码，是本次最大的坑。
Excel 导出的 csv 表头容易附带隐形空格，读取后一定要清理列名。
多文件合并时间序列数据，必须做去重、空值清洗、排序。
matplotlib 绘图必须配置中文字体，否则中文方框。
文件路径操作：先判断文件夹，不存在自动创建。
增加多层异常捕获，单个文件损坏不中断整体任务。
保存 csv 给 Windows 用户使用，建议使用 utf-8-sig 编码。