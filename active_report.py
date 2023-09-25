import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


class ActivityReport:
    def __init__(self, org):
        self.org = org
        # Read the data file
        self.active_csv = pd.read_csv(f'data/{org}/{org}_activity_details.csv')
        
        # 首先排除'Last Activity Date'列为空的行
        self.active_csv = self.active_csv.dropna(subset=['Last Activity Date'])
        # Filter the data for the last `days` days
       
       
        # recent_activity = recent_activity.dropna(subset=['Last Activity Date'])
        self.active_csv['Last Activity Date'] = self.active_csv['Last Activity Date'].apply(lambda x: x.split('+')[0])
        self.active_csv['Last Activity Date'] = pd.to_datetime(self.active_csv['Last Activity Date']) # Convert to timestamp
        # print(self.active_csv)
    # 写一个方法，分析data/{self.org}_last_activity.csv，显示最近30天，按照IDE统计的使用频率排序，并画图（饼状图）；
    def print_ide_usage(self, days=30, column='IDE', type='pie'):
        
        # print(data)
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days)
        data = self.active_csv[(self.active_csv['Last Activity Date'] >= start_date)]
        # Count the number of times each IDE was used
        column_counts = data[column].value_counts()

        # Sort the IDEs by usage frequency
        column_counts = column_counts.sort_values(ascending=False)
        # print(column_counts)
        # print(column_counts.index)
        # print(column_counts.values)
        # print(list(column_counts.index))
        # return None

        # 如果column_counts太长，会导致饼图显示不全，所以需要限制一下，只显示前10个内容
        if len(column_counts) > 10:
            column_counts = column_counts.head(10)
        # print(column_counts)
    
        matplotlib.use('Agg')
        # Plot the results as a pie chart or a bar chart based on the type parameter
        if type.upper() == 'PIE':
            plt.pie(column_counts.values, labels=column_counts.index, autopct='%1.0f%%')
            plt.title(f'{column} Usage in the Last {days} Days')
            # 在每个饼图上显示具体值
            for i, v in enumerate(column_counts.values):
                 plt.text(i, v, f"{v}", color='blue', fontsize=12, ha='center', va='center')
            plt.savefig(f'static/{self.org}/{self.org}_{column}_Pie.png')
            #plt.show()
            
        elif type.upper() == 'BAR':
            labels = list(column_counts.index)
            plt.bar(labels, column_counts.values)
            plt.title(f'{column} Usage in the Last {days} Days')
            plt.xlabel(f'{column}')
            plt.ylabel('Number of Uses')
            plt.xticks(rotation=15)
            # 在每个柱子上显示具体值
            for i, v in enumerate(column_counts.values):
                plt.text(i, v, f"{v}", color='blue', fontsize=12, ha='center', va='bottom')
            plt.savefig(f'static/{self.org}/{self.org}_{column}_Bar.png')
            

            #plt.show()
        elif type.upper() == 'REPORT':
            print(f"Index: {column_counts.index}")
            print(f"Values: {column_counts.values}")
        # 每次都是产生一个新的figure，如果不清除，会产生多个figure
        # 先判断下是否有figure存在，如果有，则清除
        if plt.fignum_exists(1):
            plt.clf()    

    # 写一个方法，分析data/{self.org}_last_activity.csv，显示最近30天，按天按人统计的每天日活用户数；
    # 首先针对Last Activity Date 列，需要分解出来Day，因为我们需要按照Day来统计，所以需要把Day单独拿出来，然后再统计
    #  拿出来的方法是：data['Last Activity Date'].apply(lambda x: x.split('T')[0]) 
    # Last Activity Date列的内容样例是，2023-09-04T16:56:59+08:00，分解出来的时间是2023-09-04
    # 然后再把这个时间转换成时间戳，data['Last Activity Date'] = pd.to_datetime(data['Last Activity Date'])
    #然后按照login,Last Activity Date分组，然后统计每组的数量，data.groupby(['login','Last Activity Date']).size()
    # 然后再按照Last Activity Date分组，统计每组的数量，data.groupby(['Last Activity Date']).size()

    def print_daily_active_users(self, days=30):
        """
        Prints the daily active users for the last `days` days and saves a scatter plot of the results.

        Args:
        - days (int): The number of days to include in the report. Default is 30.

        Returns:
        - None
        """
        data = pd.read_csv(f'data/{self.org}/{self.org}_activity_details.csv')
        # 首先排除'Last Activity Date'列为空的行
        data = data.dropna(subset=['Last Activity Date'])
        # Filter the data for the last `days` days
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days)
        data['Last Activity Date'] = data['Last Activity Date'].apply(lambda x: x.split('T')[0])
        data['Last Activity Date'] = pd.to_datetime(data['Last Activity Date'])
        data = data[(data['Last Activity Date'] >= start_date)]
        # print(data)
        # 按照login,Last Activity Date分组，然后统计每组的数量，并按照Last Activity Date排列
        data = data.groupby(['Login','Last Activity Date']).size().reset_index(name='counts').sort_values(by='Last Activity Date')
        # print(data)
        # 按照Last Activity Date分组，统计每组的数量
        data = data.groupby(['Last Activity Date']).size().reset_index(name='counts')
        # print(data)

        # Plot the results as a scatter plot
        plt.plot(data['Last Activity Date'], data['counts'], '-o')
        plt.title(f'Daily Active Users in  Last {days} Days')
        plt.xlabel('Date')
        plt.ylabel('Number of Daily Active Users')
        plt.xticks(rotation=45)
        plt.yticks(range(0, int(max(data['counts']))+10, 5))
        plt.gca().yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        plt.savefig(f'static/{self.org}/{self.org}_active_users_byday.png')
        #plt.show()
        # 清空图片
        plt.clf()