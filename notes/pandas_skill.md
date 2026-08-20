bs.login()：向 baostock 的服务器发送登录请求，这个平台必须先登录才能拿数据

lg：login 的返回结果对象，里面包含登录成功 / 失败信息

lg.error_msg：打印登录提示文字，如果成功会显示：success
⚠️ 注意：登录只是程序后台连接服务器，不需要你输入账号密码，baostock 是免注册免费使用



#and 和 &的用法
#分两块讲清楚：while 循环里 & 和 and 的本质区别，以及你遇到报错的根源
1、两个符号底层完全不是一类东西
and：Python 逻辑运算符
专门用来判断「真假条件」，两边只能是布尔值 True / False。
会先判断左边整体结果，再判断右边。
&：按位与运算符（位运算）
原本是给数字二进制计算用的；
只有在 pandas 筛选 df[(a)&(b)] 场景才用来做多条件，普通 if/while 循环不能乱用。
2、你的报错完整原因
python
运行
while rs.error_code == "0" & rs.next():
运算优先级：& 优先级 ＞ ==
代码会被计算机先算 "0" & rs.next()，再算 ==
rs.next() 返回布尔值 True/False
"0" 是字符串，布尔是 True
字符串 和 bool 不能做位运算 &，直接抛出类型报错。
但你加括号也救不了 &
哪怕写成：
python
运行
while (rs.error_code == "0") & (rs.next()):
依然不推荐、极易出问题：
布尔值 True 在底层等于数字 1，False=0
True & True → 1 & 1 =1（等价 True）
True & False →1 &0=0（等价 False）
语法能跑，但这是数字位运算，不是标准逻辑判断，属于歪路子，baostock 循环里偶尔会逻辑错乱。
3、and 为什么不会报错
and 是纯逻辑判断，运算优先级低于 ==，执行顺序天然正确：
python
运行
while rs.error_code == "0" and rs.next():
计算机执行顺序：
先算左边 rs.error_code == "0"，得到布尔 True/False
再用 and 判断右边 rs.next()
全程只做真假对比，不存在字符串、数字、布尔混算冲突，不会报类型错误。
4、终极区分记忆（必考，再也不混）
场景 1：普通判断 while /if 语句（比如你现在的循环）
只用 and（并且）、or（或者）
python
运行
while A == "0" and B:
if x>10 or x<0:
场景 2：pandas 表格多条件筛选（唯一用 &、| 的地方）
必须 &（且）、|（或），每个条件加括号
python
运行
df[(df["收盘"]>100) & (df["成交量"]>50000)]
5、补充你刚才代码的标准正确写法
python
运行
while rs.error_code == '0' and rs.next():
    data_list.append(rs.get_row_data())
永远用 and，稳定无报错，逻辑清晰。