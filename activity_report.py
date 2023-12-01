import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
from load_save_Usage import CSV_UsageDB,MySQL_UsageDB
from get_usage_fromGithub import GetUsage_FromGithub
from orgs_manger import MySQLOrgsManager, CSVOrgsManager

class ActivityReport:
    def __init__(self, org, usage_db):
        self.org = org
        self.usage_db = usage_db

    def print_daily_active_users(self, days=30):

        # Step 1: Data retrieval
        df = self.usage_db.load_active_usage(days)
        # print (f'data in daily activity before show is {df}')
        if isinstance(df, list):
            df = pd.DataFrame(df, columns=['Last Activity Date', 'counts'])
            #print (f'data after conver in print_daily_active_users  is {df}')
        
        # check the type of 'last activity date' column, if it's string, convert it to datetime
        #print(df['Last Activity Date'].dtype)   # it is datetime64[ns]
        #print(df['counts'].dtype) # it is int64

        # Step 2: Data processing and presentation
        # Convert the data to a pandas DataFrame
        #df = pd.DataFrame(data, columns=['Last Activity Date', 'counts'])

        # # Convert the dates to pandas Timestamps
        # df['Last Activity Date'] = pd.to_datetime(df['Last Activity Date'])
        # df['Last Activity Date'] = df['Last Activity Date'].dt.tz_localize(None)

        # Group by date and count the number of unique logins
        # added by zhuang on 2023/11/7. the data are already filtered by days, so no need to group by date
        # df = df.groupby('Last Activity Date').size().reset_index(name='counts')

        # Print the data
        # print(f'Last {days} days active usage:')
        # print(df)

        # 去掉时区信息，否则会报错：TypeError: tz must be string or tzinfo subclass.
        # Optionally, you can also plot the data
        
        plt.plot(df['Last Activity Date'], df['counts'])
        plt.title(f'Daily Active Users in the Last {days} Days')
        plt.xlabel('Date')
        plt.ylabel('Number of Active Users')

        plt.xticks(df['Last Activity Date'][::1], rotation=45)
        plt.yticks(range(0, int(max(df['counts']))+10, 5))
        plt.gca().yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        plt.savefig(f'static/{self.org}/{self.org}_active_users_byday.png')
        # 清空图片
        plt.clf()

       # plt.show()
    # 参考active_report.py中的print_ide_usage方法，写一个方法，分析data/{self.org}_last_activity.csv，显示最近30天，按IDE统计的IDE使用情况；
    # 而且，这个方法可以接受一个参数column，用来指定是按IDE统计，还是按Editor统计
    # 报表类型，根据type参数，可以是饼图，也可以是柱状图
    def print_ide_usage(self, column='IDE',days=30,type='pie'):
        # Step 1: Data retrieval
        self.generate_graph_byColumn(column,days,type)
        return
    
        column_counts = self.usage_db.load_usage_byColumn(column,days)

        print (f'data before show in usage report is {column_counts}')
        # from mysql, data is as below:
        #data before show in usage report is [('vscode', 42), ('VisualStudio', 2), ('JetBrains-IC', 12), ('', 1)]
        # data after convert in usage report is             IDE  count
            # 0        vscode     42
            # 1  VisualStudio      2
            # 2  JetBrains-IC     12
            # 3                    1
        # from csv, data is as below:
        #data before show in usage report is Copilot-Feature
            # copilot-chat        94
            # copilot-intellij    28
            # copilot             12
            # copilot-vs           3
        
        # Convert the data to a pandas DataFrame
        # Check the type of column_counts
        if isinstance(column_counts, list):
        # If it's a list, convert it to a DataFrame
            column_counts = pd.DataFrame(column_counts, columns=[column, 'count'])
            print (f'data after convert in usage report is {column_counts}')

        if len(column_counts) > 10:
            column_counts = column_counts.head(10)
        # print(column_counts)
    
        matplotlib.use('Agg')
        # Plot the results as a pie chart or a bar chart based on the type parameter
        if type.upper() == 'PIE':
            #plt.pie(column_counts.values, labels=column_counts.index, autopct='%1.0f%%')
            plt.pie(column_counts['count'].values, labels=column_counts[column].values, autopct='%1.0f%%')
            plt.title(f'{column} Usage in the Last {days} Days')
            # 在每个饼图上显示具体值
            # for i, v in enumerate(column_counts.values):
            #      plt.text(i, v, f"{v}", color='blue', fontsize=12, ha='center', va='center')
            for i, (ide, count) in enumerate(column_counts.values):
                plt.text(i, count, f"{count}", color='blue', fontsize=12, ha='center', va='center')
            plt.savefig(f'static/{self.org}/{self.org}_{column}_Pie.png')
           # plt.show()
            
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

    def generate_graph_byColumn(self, column='IDE', days=30, type='pie'):
        # Load the usage data
        column_counts = self.usage_db.load_usage_byColumn(column, days)

    #    print (f'data before show in column report is {column_counts}')
        # Check the type of column_counts
        if isinstance(column_counts, list):
            # If it's a list, convert it to a DataFrame
            column_counts = pd.DataFrame(column_counts, columns=[column, 'count'])
            print (f'data after convert in column report is {column_counts}')

        # 如果column_counts太长，会导致饼图显示不全，所以需要限制一下，只显示前10个内容
        if len(column_counts) > 10:
            column_counts = column_counts.head(10)
        
        matplotlib.use('Agg')
        x = range(len(column_counts))
        y = column_counts['count'].values
        labels = column_counts[column].values
        # Check the type parameter
        if type == 'pie':
            # If it's 'pie', generate a pie chart
            plt.pie(column_counts['count'].values, labels=column_counts[column].values, autopct='%1.0f%%')
        elif type == 'bar':
            # If it's 'bar', generate a bar chart
            plt.figure(figsize=(10, 6))  # Increase the figure size
            plt.bar(x, y)
            plt.xticks(x, labels, rotation=30)  # Adjust the rotation angle to 90 degrees
            plt.xlabel(column)
            plt.ylabel('Count')
        elif type.lower() == 'report':
            print(f"Index: {column_counts.index}")
            print(f"Values: {column_counts.values}")
        # Save the figure
        plt.savefig(f'static/{self.org}/{self.org}_{column}_{type}.png')

        # Show the figure
        # plt.show()
        if plt.fignum_exists(1):
            plt.clf()   