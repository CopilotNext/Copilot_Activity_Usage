import matplotlib
import pandas as pd
import matplotlib.pyplot as plt

class LastActivityReport:
    def __init__(self, org):
        self.org = org
        self.recent_activity = pd.read_csv(f'data/{self.org}/{self.org}_last_activity.csv')
        self.row_count = len(self.recent_activity)
        self.row_count_not_null = len(self.recent_activity.dropna(subset=['Last Activity Date']))
    
    def print_null_last_activity(self):
        # 读取recent_activity.csv文件
        recent_activity = self.recent_activity

        # 获取指定Login的数据,并且'Last Activity Date'列为空
        login_data = recent_activity[recent_activity['Last Activity Date'].isnull()]
        # 只保留'Login'和'Last Activity Date'两列
        # login_data = login_data[['Login', 'Last Activity Date']]
        login_data = login_data[['Login']]

        # 打印结果
        print(f"Number of rows with null 'Last Activity Date': {len(login_data)}")
        return(login_data)


    def print_last_activity_over_days(self, days=7):
        # 读取recent_activity.csv文件
        # recent_activity = pd.read_csv(f'data/{self.org}_last_activity.csv')
        recent_activity = self.recent_activity

        # 首先排除'Last Activity Date'列为空的行
        recent_activity = recent_activity.dropna(subset=['Last Activity Date'])

        # recent_activity = recent_activity.dropna(subset=['Last Activity Date'])
        #recent_activity['Last Activity Date'] = recent_activity['Last Activity Date'].apply(lambda x: x.split('+')[0])
        recent_activity.loc[:, 'Last Activity Date'] = recent_activity['Last Activity Date'].apply(lambda x: x.split('+')[0])
        recent_activity.loc[:, 'Last Activity Date'] = pd.to_datetime(recent_activity['Last Activity Date'])
        # df['Last Activity Date'] = df['Last Activity Date'].str[:19]

        # 将'Last Activity Date'列转换为datetime类型
        recent_activity['Last Activity Date'] = pd.to_datetime(recent_activity['Last Activity Date'])

        # 获取指定天数前的日期
        query_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        print(f"query_date: {query_date}")

        # 获取指定天数前的数据
        recent_activity = recent_activity[recent_activity['Last Activity Date'] < query_date]

        # 只保留'Login'和'Last Activity Date'两列
        login_data = recent_activity[['Login', 'Last Activity Date']]

        # 打印结果
        print(f"Number of rows over {days} days not used : {len(login_data)}")
        return login_data
    
    def print_active_user(self):
        # 读取recent_activity.csv文件
        recent_activity = self.recent_activity

        # 得到recent_activity中的行数
        row_count = len(recent_activity)

        # 得到recent_activity，'Last Activity Date'列不为空的行数
        row_count_not_null = len(recent_activity.dropna(subset=['Last Activity Date']))

        # 画图，并展现结果，显示row_count和row_count_not_null的比例
        labels = ['Not Used', 'Used']
        sizes = [row_count - row_count_not_null, row_count_not_null]
        matplotlib.use('Agg')
        
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f"{self.org} Last Activity Usage")
        # 保存图片
        plt.savefig(f"static/{self.org}/{self.org}_Last_Activity_usage.png")
        #plt.show()
        # 清空图片
        plt.clf()
        


# report = LastActivityReport(org)
# # report.print_last_activity_over_days(7)
# # report.print_active_user()
# print(report.row_count_not_null)
# print(report.row_count)

    
