import os
import csv
import datetime
import pandas as pd
from get_usage_fromGithub import GetUsage_FromGithub
from orgs_manger import MySQLOrgsManager, CSVOrgsManager

class UsageDB:
    def __init__(self, org_name):
        self.org_name = org_name
        self.now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        self.savepath=f'data/{self.org_name}'
        #self.filename = f"{self.savepath}/{self.org_name}_{self.now}"
        

    def save_usage(self, assignees=None):
        self.__save_now_activity(assignees) #{org_name}_{now().csv or table
        self.__save_last_activity(assignees) #{org_name}_last_activity.csv or table
        self.__save_now_active(assignees)    #{org_name}_{now()}_active.csv or table
        self.__merge_now_active(assignees)   #{org_name}_activity.csv or table
        self.__save_now_details(assignees)   #{org_name}_{now()}_active_details.csv or table
        self.__merge_details(assignees)    #{org_name}_activity_details.csv or table      

    
    def __save_now_activity(self, assignees):
        # Implementation of save_now_activity
        pass

    def __save_last_activity(self, assignees):
        # Implementation of save_last_activity
        pass

    def __save_now_active(self, assignees):
        # Implementation of save_now_active
        pass
 
    def __merge_now_active(self, assignees):
        # Implementation of merge_now_active
        pass

    def __save_now_details(self, assignees):
        # Implementation of save_now_details
        pass

    def __merge_details(self, assignees):
        # Implementation of merge_details
        pass

    def load_active_usage(self,days=30):
        raise NotImplementedError

    def load_last_activity(self):
        raise NotImplementedError
    
    def load_usage_byColumn(self,column,days=30):
        raise NotImplementedError

class MySQL_UsageDB(UsageDB):
    def __init__(self, org_name,connection):
        org_name = org_name.replace('-', '_')  # 将破折号替换为下划线;因为MySQL不允许在表名中使用破折号
        super().__init__(org_name)
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.init_org()

    def init_org(self):
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.org_name}_last_activity (id INT NOT NULL,Login VARCHAR(255) PRIMARY KEY, Last_Activity_Date TIMESTAMP, Last_Editor_Used VARCHAR(255))")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.org_name}_history_activity (id INT NOT NULL,Login VARCHAR(255), Last_Activity_Date TIMESTAMP, Last_Editor_Used VARCHAR(255),Refresh_Date TIMESTAMP)")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.org_name}_activity (id INT NOT NULL,Login VARCHAR(255) NOT NULL, Last_Activity_Date TIMESTAMP, Last_Editor_Used VARCHAR(255))")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.org_name}_activity_details (id INT NOT NULL,Login VARCHAR(255) NOT NULL, Last_Activity_Date TIMESTAMP,IDE VARCHAR(255),`IDE Version` VARCHAR(255),`Copilot-Feature` VARCHAR(255),`Copilot-Version` VARCHAR(255))")
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred while initializing MySQL tables: {e}")

    def save_usage(self, assignees=None):
        if assignees is None or len(assignees) == 0:
            print(f'Info: No assignees,will fetch from github - {assignees}')
            # call github api to get assignees
            # get the access_token from the database
            orgs_manager = MySQLOrgsManager(self.connection)
            # since the org_name is replaced by org_name.replace('-', '_') in __init__, so we need to replace it back
            # because in github, it is still org_name
            org_name_original = self.org_name.replace('_', '-')
            access_code = orgs_manager.get_org_access_code(org_name_original)
            if access_code is None:
                print(f'Error: No access_code for org in save_usage {org_name_original}')
                return
            # call github api to get assignees
            assignees=GetUsage_FromGithub(org_name_original, access_code).extract_copilot_by_org()
            #print(f"assignees was got successfully for org in save_usage: {org_name_original}； ")
        self.__save_last_activity(assignees) #{org_name}_last_activity.csv or table
        self.__save_now_activity(assignees) #{org_name}_{now().csv or table
        self.__save_now_active(assignees)    #{org_name}_{now()}_active.csv or table
        self.__merge_now_active(assignees)   #{org_name}_activity.csv or table
        self.__save_now_details(assignees)   #{org_name}_{now()}_active_details.csv or table
        self.__merge_details(assignees)    #{org_name}_activity_details.csv or table     
      

    
    def __save_now_activity(self, assignees):
        # Implementation of save_now_activity
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"now is {now}， it will be saved as Refresh_Date in {self.org_name}_history_activity")
        try:
            sql = f"""
            INSERT INTO {self.org_name}_history_activity (id, Login, Last_Activity_Date, Last_Editor_Used, Refresh_Date)
            SELECT id, Login, Last_Activity_Date, Last_Editor_Used, '{now}' AS Refresh_Date
            FROM {self.org_name}_last_activity
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred while saving history Activity to DB: {e}")

    def __save_last_activity(self, assignees):
        # Implementation of save_last_activity
        #try:
            # Delete all data from the table
            self.cursor.execute(f"DELETE FROM {self.org_name}_last_activity")
            self.connection.commit()
            for usage in assignees:
                sql = f"INSERT INTO {self.org_name}_last_activity (id, Login, Last_Activity_Date, Last_Editor_Used) VALUES (%s, %s, %s, %s)"
                values = (usage[0], usage[1], usage[2], usage[3])
                self.cursor.execute(sql, values)
            self.connection.commit()
        #except Exception as e:
        #    print(f"An error occurred while saving last Activity to DB: {e}")

    def __save_now_active(self, assignees):
        # Implementation of save_now_active
        pass

    def __merge_now_active(self, assignees):
        # Implementation of merge_now_active
        try:
            query = f"""
            INSERT INTO {self.org_name}_activity (id, Login, Last_Activity_Date, Last_Editor_Used)
            SELECT id, Login, Last_Activity_Date, Last_Editor_Used
            FROM {self.org_name}_last_activity
            WHERE Last_Activity_Date IS NOT NULL
            AND NOT EXISTS (
                SELECT 1
                FROM {self.org_name}_activity
                WHERE {self.org_name}_activity.Login = {self.org_name}_last_activity.Login
                AND {self.org_name}_activity.Last_Activity_Date = {self.org_name}_last_activity.Last_Activity_Date
            )
            """
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred while merging now active to DB: {e}")

    def __save_now_details(self, assignees):
        # Implementation of save_now_details
        pass

    def __merge_details(self, assignees):
        # Implementation of merge_details
        try:
            query = f"""
            INSERT INTO {self.org_name}_activity_details (id, Login, Last_Activity_Date, IDE, `IDE Version`, `Copilot-Feature`, `Copilot-Version`)
            SELECT id, Login, Last_Activity_Date,
                SUBSTRING_INDEX(Last_Editor_Used, '/', 1) AS IDE,
                SUBSTRING_INDEX(SUBSTRING_INDEX(Last_Editor_Used, '/', -3), '/', 1) AS `IDE Version`,
                SUBSTRING_INDEX(SUBSTRING_INDEX(Last_Editor_Used, '/', -2), '/', 1) AS `Copilot-Feature`,
                SUBSTRING_INDEX(Last_Editor_Used, '/', -1) AS `Copilot-Version`
            FROM {self.org_name}_last_activity
            WHERE Last_Activity_Date IS NOT NULL
            AND NOT EXISTS (
                SELECT 1
                FROM {self.org_name}_activity_details
                WHERE {self.org_name}_activity_details.Login = {self.org_name}_last_activity.Login
                AND {self.org_name}_activity_details.Last_Activity_Date = {self.org_name}_last_activity.Last_Activity_Date
            )
            """
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred while merging details to DB: {e}")
    
    def load_active_usage(self, days=30):
        # Calculate the date days days ago
        query = f"""
        SELECT DATE(`Last_Activity_Date`) as `Last Activity Date`, COUNT(DISTINCT Login) as counts
        FROM {self.org_name}_activity
        WHERE DATE(`Last_Activity_Date`) >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY DATE(`Last_Activity_Date`)
        ORDER BY DATE(`Last_Activity_Date`)
        """
        self.cursor.execute(query)

        # Fetch all the rows
        data = self.cursor.fetchall()

        # Convert the dates to strings in the desired format
        data = [(date.strftime('%Y/%m/%d'), count) for date, count in data]
        #print(data)
        return data
    
        #[('2023/11/03', 11), ('2023/11/05', 1), ('2023/11/06', 10)]#

    def load_last_activity(self):
        # Execute the SQL query
        #query = f"SELECT * FROM {self.org_name}_last_activity ORDER BY Last_Activity_Date DESC"
        query = f"SELECT id, Login, Last_Activity_Date AS `Last Activity Date`, Last_Editor_Used AS `Last Editor Used` FROM {self.org_name}_last_activity ORDER BY Last_Activity_Date DESC"
        self.cursor.execute(query)
        # Fetch the row
        data = self.cursor.fetchall()

        return data

    def load_usage_byColumn(self, column='IDE', days=30):
    
        # Execute the SQL query
        query = f"""
            SELECT `{column}`, COUNT(*) as counts
            FROM {self.org_name}_activity_details
            WHERE `Last_Activity_Date` >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
            GROUP BY `{column}`
        """
        self.cursor.execute(query)

        # Fetch all the rows
        data = self.cursor.fetchall()

        return data


class CSV_UsageDB(UsageDB):
    def __init__(self, org_name):
        super().__init__(org_name)
        self.init_org()


    def init_org(self):
        try:
            os.makedirs(f'static/{self.org_name}', exist_ok=True)
            os.makedirs(f'data/{self.org_name}', exist_ok=True)
        except Exception as e:
            print(f"An error occurred while creating directories: {e}")

    def save_usage(self, assignees=None):
        # if assignees is None or len(assignees) == 0, just return
        if assignees is None or len(assignees) == 0:
            print(f'Info: No assignees, will fetch it - {assignees}')
            # call orgs_manager to get access_code
            orgs_manager = CSVOrgsManager('data/orgs.csv')
            access_code = orgs_manager.get_org_access_code(self.org_name)
            # call github api to get assignees
            assignees=GetUsage_FromGithub(self.org_name, access_code).extract_copilot_by_org()
            print(f"assignees was got successfully for org in save_usage: {self.org_name}； ")
        self.__save_now_activity(assignees) #{org_name}_{now().csv or table
        self.__save_last_activity(assignees) #{org_name}_last_activity.csv or table
        self.__save_now_active(assignees)    #{org_name}_{now()}_active.csv or table
        self.__merge_now_active(assignees)   #{org_name}_activity.csv or table
        self.__save_now_details(assignees)   #{org_name}_{now()}_active_details.csv or table
        self.__merge_details(assignees)    #{org_name}_activity_details.csv or table        

    
    
    def __save_now_activity(self, assignees):
        # Implementation of save_now_activity
        filename = f"{self.savepath}/{self.org_name}_{self.now}.csv"
        # save seatsusage from assignees to csv
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
            for assignee in assignees:
                writer.writerow(assignee)
        print(f"save_now_activity was got successfully for org: {self.org_name}； ")

    def __save_last_activity(self, assignees):
        # Implementation of save_last_activity
        # save seatsusage from assignees to csv， since the now_activity is the last_activity, copy and save it to last_activity
        org_last_activity_filename = f"{self.savepath}/{self.org_name}_last_activity.csv"
        with open(org_last_activity_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
            for assignee in assignees:
                writer.writerow(assignee)

    def __save_now_active(self, assignees):
        # Implementation of save_now_active
        # filter the seatsusage from assignees to active_assignees
        #filtered_assignees = [a for a in assignees if a['Last_Activity_Date'] is not None]
        filtered_assignees = [a for a in assignees if a[2] is not None]
        with open(f"{self.savepath}/{self.org_name}_{self.now}_active.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
            for assignee in filtered_assignees:
                writer.writerow(assignee)


    def __merge_now_active(self, assignees):
        # Implementation of merge_now_active
        #filtered_assignees = [a for a in assignees if a['Last_Activity_Date'] is not None]
        filtered_assignees = [a for a in assignees if a[2] is not None]
        filename = f"{self.savepath}/{self.org_name}_activity.csv"
        # save filtered_assignees to csv
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                for assignee in filtered_assignees:
                    writer.writerow(assignee)
        else:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                if filtered_assignees:
                    writer.writerow(['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
                    for assignee in filtered_assignees:
                        writer.writerow(assignee)
        # remove duplicates based on Login and Last Activity Date
        df = pd.read_csv(filename)
        df.drop_duplicates(subset=['Login', 'Last Activity Date'], keep='last', inplace=True)
        df.to_csv(filename, index=False)
        print(f"__merge_now_active was got successfully for org: {self.org_name}； ")

    def __save_now_details(self, assignees):
        filtered_assignees = [a for a in assignees if a[2]]  # Filter out assignees where "Last Activity Date" is None
        with open(f"{self.savepath}/{self.org_name}_{self.now}_active_details.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'Login', 'Last Activity Date', 'IDE', 'IDE Version', 'Copilot-Feature', 'Copilot-Version'])
            for assignee in filtered_assignees:
                if assignee[3]:  # If "Last Editor Used" is not None
                    split_data = assignee[3].split('/')
                    if len(split_data) == 4:  # If "Last Editor Used" can be split into four parts
                        writer.writerow(assignee[:3] + split_data)
                    else:
                        writer.writerow(assignee[:3] + [None, None, None, None])

    def __merge_details(self, assignees):
            # Implementation of merge_details
            #filtered_assignees = [a for a in assignees if a['Last_Activity_Date'] is not None]
            filtered_assignees = [a for a in assignees if a[2] is not None]
            filename = f"{self.savepath}/{self.org_name}_activity_details.csv"
            # save filtered_assignees to csv
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    for assignee in filtered_assignees:
                        #if assignee['Last_Editor_Used']:  # If "Last Editor Used" is not None
                        if assignee[3]:  # If "Last Editor Used" is not None
                            split_data = assignee[3].split('/')
                            if len(split_data) == 4:  # If "Last Editor Used" can be split into four parts
                                #writer.writerow([assignee['id'], assignee['Login'], assignee['Last_Activity_Date']] + split_data)
                                writer.writerow([assignee[0], assignee[1], assignee[2]] + split_data)
                            else:
                                writer.writerow([assignee[0], assignee[1], assignee[2]] + [None, None, None, None])
                        else:
                            writer.writerow([assignee[0], assignee[1], assignee[2]] + [None, None, None, None])
            else:
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    if filtered_assignees:
                        writer.writerow(['id', 'Login', 'Last Activity Date', 'IDE', 'IDE Version', 'Copilot-Feature', 'Copilot-Version'])
                        for assignee in filtered_assignees:
                            #if assignee['Last_Editor_Used']:  # If "Last Editor Used" is not None
                            if assignee[3]:  # If "Last Editor Used" is not None
                                split_data = assignee[3].split('/')
                                if len(split_data) == 4:  # If "Last Editor Used" can be split into four parts
                                    writer.writerow([assignee[0], assignee[1], assignee[2]] + split_data)
                                else:
                                    writer.writerow([assignee[0], assignee[1], assignee[2]] + [None, None, None, None])
                            else:
                                writer.writerow([assignee[0], assignee[1], assignee[2]]+ [None, None, None, None])
            # remove duplicates based on Login and Last Activity Date
            df = pd.read_csv(filename)
            df.drop_duplicates(subset=['Login', 'Last Activity Date'], keep='last', inplace=True)
            df.to_csv(filename, index=False)
            print(f"__merge_details was got successfully for org: {self.org_name}； ")

    def load_active_usage(self,days=30):
        # Implementation for CSV files
        # data = []
        # with open(f'{self.savepath}/{self.org_name}_activity.csv', 'r') as f:
        #     reader = csv.DictReader(f)
        #     for row in reader:
        #         data.append(row)
        # return data
        
        data = pd.read_csv(f'{self.savepath}/{self.org_name}_activity_details.csv')
        # 首先排除'Last Activity Date'列为空的行，虽然这里的数据已经在save_now_details()中排除了，但是还是加上这一步，以防万一
        data = data.dropna(subset=['Last Activity Date'])
        # Filter the data for the last `days` days
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days)
        data['Last Activity Date'] = data['Last Activity Date'].apply(lambda x: x.split('T')[0])
        data['Last Activity Date'] = pd.to_datetime(data['Last Activity Date'])
        data = data[(data['Last Activity Date'] >= start_date)]
        #print(data)
        # 按照login,Last Activity Date分组，然后统计每组的数量，并按照Last Activity Date排列
        data = data.groupby(['Login','Last Activity Date']).size().reset_index(name='counts').sort_values(by='Last Activity Date')
        # print(data)
        # 按照Last Activity Date分组，统计每组的数量
        data = data.groupby(['Last Activity Date']).size().reset_index(name='counts')
        # print(data)
        return data


    def load_last_activity(self):
        # Implementation for CSV files
        df = pd.read_csv(f'{self.savepath}/{self.org_name}_last_activity.csv')

        # Check if 'Last Activity Date' column contains '+', if so, convert it to datetime
        if df['Last Activity Date'].str.contains('\+').any():
            #首先获得+号前面的内容，然后转换为datetime
            #df['Last Activity Date'] = df['Last Activity Date'].apply(lambda x: x.split('+')[0])
            df['Last Activity Date'] = df['Last Activity Date'].apply(lambda x: x.split('+')[0] if isinstance(x, str) else x)
            df['Last Activity Date'] = pd.to_datetime(df['Last Activity Date'])
            
        data = df.to_dict('records')
        return data
    
    def load_usage_byColumn(self,column='',days=30):
       # print(data)
        end_date = pd.Timestamp.now()
        days = int(days)
        start_date = end_date - pd.Timedelta(days=days)
        data = pd.read_csv(f'{self.savepath}/{self.org_name}_activity_details.csv')
        # 首先排除'Last Activity Date'列为空的行，虽然这里的数据已经在save_now_details()中排除了，但是还是加上这一步，以防万一
        data = data.dropna(subset=['Last Activity Date'])
        # recent_activity = recent_activity.dropna(subset=['Last Activity Date'])
        data['Last Activity Date'] = data['Last Activity Date'].apply(lambda x: x.split('+')[0])
        data['Last Activity Date'] = pd.to_datetime(data['Last Activity Date']) # Convert to timestamp
        # with the data,Filter the data for the last `days` days from start_date, and then group by column and count the number of the column
        data=data[(data['Last Activity Date'] >= start_date)]
        #data = self.active_csv[(self.active_csv['Last Activity Date'] >= start_date)]

        # Count the number of times each IDE was used
        column_counts = data[column].value_counts()
        column_counts = data[column].value_counts().reset_index()
        column_counts.columns = [column, 'count']

        # Sort the IDEs by usage frequency
        column_counts = column_counts.sort_values(by='count',ascending=False)
        # print(column_counts)
        # print(column_counts.index) #Index(['vscode', 'JetBrains-IC', 'VisualStudio'], dtype='object', name='IDE')
        # print(column_counts.values) #[93 24  3]
        # print(list(column_counts.index)) #['vscode', 'JetBrains-IC', 'VisualStudio']
        

        # 如果column_counts太长，会导致饼图显示不全，所以需要限制一下，只显示前10个内容
        if len(column_counts) > 10:
            column_counts = column_counts.head(10)
        
        return column_counts
    

