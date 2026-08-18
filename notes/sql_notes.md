markdown
# SQL 学习笔记
>练习数据表：stock_data
>字段：date(日期)、open(开盘价)、close(收盘价)、volume(成交量)、year(年份)

## 一、基础查询 SELECT
语法
```sql
SELECT 列名1, 列名2 FROM 表名;

* 代表查询所有列
sql
SELECT * FROM stock_data;
AS 给列起别名
sql
SELECT date AS 交易日, close AS 收盘价 FROM stock_data;
二、条件筛选 WHERE
筛选原始表里面的行，分组之前使用
运算符：> < >= <= = <>
sql
SELECT date, close FROM stock_data WHERE close > 220;
多条件 AND / OR
AND：两个条件同时成立
OR：满足任意一个条件
sql
SELECT date, close, volume 
FROM stock_data 
WHERE close > 220 AND volume < 800000;
BETWEEN 区间查询
包含区间两端的值
sql
SELECT close FROM stock_data WHERE close BETWEEN 200 AND 225;
三、排序 ORDER BY
DESC：降序（从高到低）
ASC：升序（从低到高，默认可省略）
sql
SELECT * FROM stock_data ORDER BY close DESC;
四、LIMIT 限制返回行数
只取出前 N 条数据
sql
SELECT close, volume 
FROM stock_data 
WHERE close BETWEEN 210 AND 230 AND volume > 1500000 
LIMIT 10;
五、聚合函数
COUNT(*)：统计行数
SUM(字段)：求和
AVG(字段)：求平均值
MAX(字段)：最大值
MIN(字段)：最小值
示例
sql
--总行数
SELECT COUNT(*) FROM stock_data;
--最高、最低收盘价
SELECT MAX(close), MIN(close) FROM stock_data;
--成交量总和
SELECT SUM(volume) FROM stock_data;
--收盘价大于220的数据条数
SELECT COUNT(*) FROM stock_data WHERE close > 220;
--成交量平均值并设置别名
SELECT AVG(volume) AS 平均成交量 FROM stock_data;
六、分组 GROUP BY
SELECT 中非聚合字段，必须出现在 GROUP BY 后面
sql
SELECT year, AVG(close) AS 年平均收盘价 
FROM stock_data 
GROUP BY year;
七、分组后筛选 HAVING
对 GROUP BY 聚合之后的结果进行筛选
WHERE：分组前筛原始数据；HAVING：分组后筛聚合结果
sql
SELECT year, SUM(volume) AS 年成交量总和 
FROM stock_data 
GROUP BY year 
HAVING 年成交量总和 > 5000000;
易错点清单
AND 只能放在 WHERE 里做条件，不能用来隔开查询字段，字段之间用英文逗号 ,
AS 别名不能写到聚合函数 AVG() / SUM() 的括号内部
HAVING 后面不能直接写字段名，需要写聚合函数或者聚合结果别名
所有符号：逗号、大于小于号必须是英文符号


## 八、DISTINCT 去重
取出一列里面不重复的值
```sql
SELECT DISTINCT 列名 FROM 表名;

LIKE 模糊查询 + 通配符
%：匹配任意长度、任意字符（可以 0 个字符）
_：匹配1 个任意字符

--开头匹配
SELECT date, close FROM stock_data WHERE date LIKE '2025-01%';

--包含匹配（中间有）
SELECT * FROM stock_data WHERE date LIKE '%-03-%';

易错点
LIKE 前面必须写字段名，不能写 WHERE * LIKE ...
开头匹配：'关键词%'
结尾匹配：'%关键词'
任意位置包含：'%关键词%'
数字等值判断优先用 =，不用 LIKE