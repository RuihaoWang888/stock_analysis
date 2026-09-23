# SQL 基础笔记（可直接复制保存为 SQL_Base.md）
> 学习目标：看懂需求、写出查询；开发思路：先实现功能，再优化。
> 书写顺序 和 **数据库执行顺序不一样**，这是 SQL 最核心考点。

## 1. 基础概念
- SQL：结构化查询语言，操作关系型数据库（MySQL / SQLite / PostgreSQL）
- Database：数据库，多张表的集合
- Table：表，类似 Excel 工作表
- Row：行 / 记录；Column：列 / 字段
- SQL 大小写不敏感，**关键字推荐大写**提升可读性

## 2. SQL 语句顺序
### ✍️ 书写顺序（你写代码的顺序）
```sql
SELECT 字段
FROM 表名
WHERE 行过滤条件
GROUP BY 分组字段
HAVING 分组后的过滤
ORDER BY 排序
LIMIT 限制行数;
```

⚡ **数据库执行顺序（重点！）**
`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`

> 关键点区分
> - `WHERE`：分组**之前**过滤原始行，**不能使用聚合函数**
> - `HAVING`：分组**之后**过滤分组结果，**可以使用聚合函数**

## 3. SELECT 查询字段
```sql
-- 查询指定列
SELECT name, price FROM goods;

-- 查询全部列
SELECT * FROM goods;

-- 字段别名 AS，AS可以省略
SELECT name AS 商品名, price 价格 FROM goods;

-- 计算列
SELECT name, age+1 AS next_age FROM student;
```

## 4. WHERE 条件过滤行
运算符：`=` `!=` `>` `<` `>=` `<=`
逻辑符：`AND`（并且）、`OR`（或者）、`NOT`（取反）
区间：`字段 BETWEEN a AND b`（包含两端，只能用于**同一个字段**区间）
模糊匹配：`LIKE`，`%`任意多字符，`_`单个字符

```sql
-- 年龄大于18，名字等于张三
SELECT * FROM student WHERE age > 18 AND name = '张三';

-- 名字包含张三（张三丰也会命中）
SELECT * FROM student WHERE name LIKE '%张三%';

-- 年龄18~25之间
SELECT * FROM student WHERE age BETWEEN 18 AND 25;
```

## 5. ORDER BY 排序
`ASC` 升序（默认），`DESC` 降序
```sql
-- 按年龄降序
SELECT * FROM student ORDER BY age DESC;
```

## 6. LIMIT 限制返回行数
```sql
-- 取前3条
SELECT * FROM student ORDER BY age ASC LIMIT 3;

-- 跳过2条，取3条（偏移2） LIMIT offset, count
SELECT * FROM student LIMIT 2,3;
```

## 7. 聚合函数 + GROUP BY + HAVING
常用聚合函数
- `COUNT(*)`：统计行数
- `SUM()`：求和
- `AVG()`：平均值
- `MAX()`：最大值
- `MIN()`：最小值

> GROUP BY 规则：SELECT 后面只能写 **分组字段 + 聚合函数**
```sql
-- 按班级分组，统计每个班级人数，只保留人数>2的班级
SELECT class_id, COUNT(*) FROM student GROUP BY class_id HAVING COUNT(*) > 2;
```

## 8. 多表连接 JOIN（高频重点）
> 表说明
> student：`id, name, age, class_id`（学生表，外键 class_id）
> class：`id, class_name`（班级表，主键 id）

| 连接类型 | 作用 |
| ---- | ---- |
| `A LEFT JOIN B` | 保留A表全部数据，匹配B；匹配不到B字段为NULL |
| `A RIGHT JOIN B` | 保留B表全部数据，匹配A；匹配不到A字段为NULL |
| `A INNER JOIN B` | 只保留两边能匹配上的数据，交集 |

✅ 规范：**ON 使用主键、外键关联，不要用文本名称关联**
> 开发习惯：优先使用 LEFT JOIN，尽量避免 RIGHT JOIN，可读性差。

```sql
-- 查询所有学生，带出班级名称（学生全部保留）
SELECT s.name, c.class_name
FROM student s
LEFT JOIN class c 
ON s.class_id = c.id;

-- 查询所有班级，带出学生姓名（班级全部保留）
SELECT c.class_name, s.name
FROM class c
LEFT JOIN student s
ON c.id = s.class_id;
```

## 9. DML 增删改（⚠️高危！）
```sql
-- 插入
INSERT INTO student(name,age) VALUES ('李四',20);

-- 更新，必须加WHERE，否则全表更新！
UPDATE student SET age=21 WHERE name='李四';

-- 删除，必须加WHERE，否则删除整张表！
DELETE FROM student WHERE name='李四';
```

## 10. 错题复盘（你的易错点）
1. ❌ `WHERE BETWEEN age>18 AND ...`
   ✅ BETWEEN 语法：字段 BETWEEN 最小值 AND 最大值，只用于单字段区间
2. ❌ 精确匹配名字用 `LIKE '%张三%'`
   ✅ 精确相等用 `=`；模糊搜索才用 LIKE
3. ❌ JOIN 的 ON 条件使用名字文本关联
   ✅ JOIN ON 使用主键、外键ID关联
4. ❌ LEFT JOIN 左右表写反：想要保留哪张表，哪张表放左边

---

你把这份笔记存进项目里的 README.md 或者单独新建 `SQL_Base.md` 就可以。
等你复习完随时喊我，我们继续做综合练习题，加油👍！