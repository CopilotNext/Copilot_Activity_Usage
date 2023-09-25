from datetime import datetime
import pandas as pd

# 读取CSV文件，文件在当前目录目录下，名字为'Lilith-Dislyte_activity.csv'
df = pd.read_csv('data\Lilith-Dislyte_last_activity.csv')

# 首先排除'Last Activity Date'列为空的行
df = df.dropna(subset=['Last Activity Date'])

# 舍弃'Last Activity Date'列的时区信息，即只保留'2023-09-04T10:27:03'部分
# 默认情况下，'Last Activity Date'列的数据格式为'2023-09-04T10:27:03+08:00'，所以需要处理
df['Last Activity Date'] = df['Last Activity Date'].apply(lambda x: x.split('+')[0])


# df['Last Activity Date'] = df['Last Activity Date'].str[:19]

# 将'Last Activity Date'列转换为datetime类型
df['Last Activity Date'] = pd.to_datetime(df['Last Activity Date'])

# 查询'Last Activity Date'列中大于等于'2023-09-04 23:30:00'的行
from datetime import datetime

# 获取当前时间
now = datetime.now()

# 将当前时间转换为字符串，并截取需要的部分
from datetime import timedelta

# 获取7天前的时间
query_date = now - timedelta(days=7)

# 查询条件是query_data之前的7天
result = df[df['Last Activity Date'] > query_date]

# 输出结果
print(result)

# 输出结果
print(result)