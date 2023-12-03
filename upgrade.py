
import mysql.connector
import pandas as pd
import create_factory

def func_test():
    # Connect to the database
    cnx = mysql.connector.connect(
        host="localhost",
        user="zhuang",
        password="copilotusage",
        database="quickstartdb"
    )
    org_name = "Demo"
    # Execute a query
    cursor = cnx.cursor()
    """ query = ("SELECT * FROM inventory")
    cursor.execute("SELECT * FROM inventory") """
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {org_name}_last_activity (id INT,Login VARCHAR(255) PRIMARY KEY, Last_Activity_Date TIMESTAMP, Last_Editor_Used VARCHAR(255))")

    # 读取 CSV 文件
    csv_file = '.\data\Demo_last_activity.csv'
    df = pd.read_csv(csv_file, header=None, names=['id', 'Login', 'Last_Activity_Date', 'Last_Editor_Used'])

    # 插入数据到 MySQL 表中
    for row in df.itertuples():
        query = f"INSERT INTO {org_name}_last_activity (id, Login, Last_Activity_Date, Last_Editor_Used) VALUES (%s, %s, %s, %s)"
        values = (row.id, row.Login, row.Last_Activity_Date, row.Last_Editor_Used)
        cursor.execute(query, values)

    # 提交更改并关闭连接
    cnx.commit()
    cursor.close()
    cnx.close()



import pandas as pd
import mysql.connector
import pandas as pd
import mysql.connector
import numpy as np

def insert_data_to_mysql(csv_file, db_config, table_name):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file, header=None, names=['id', 'Login', 'Last_Activity_Date', 'Last_Editor_Used'], skiprows=1)

    # 连接到 MySQL 数据库
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    print ("db connected，delete current data begin")
    # 插入数据到 MySQL 表中
    cursor.execute(f"delete from {table_name}")
    print ("db connected，delete current data end ")
    for row in df.itertuples():
        if pd.isna(row.Last_Activity_Date): # or isinstance(row.Last_Activity_Date, str):
            # only get the id and Login columns for rows with  invalid Last_Activity_Date values
            values = (row.id, row.Login,None,None)
        else:   
            values = (row.id, row.Login, row.Last_Activity_Date, row.Last_Editor_Used)
        query = f"INSERT INTO {table_name} (id, Login, Last_Activity_Date, Last_Editor_Used) VALUES (%s, %s, %s, %s)"
        # print("this is Values" + values)
        cursor.execute(query, values)

    # 提交更改并关闭连接
    cnx.commit()
    cursor.close()
    cnx.close()

csv_file = '.\data\Demo\Demo_last_activity.csv'
db_config = {'user': 'zhuang', 'password': 'copilotusage', 'host': 'localhost', 'database': 'copilot_usage'}
table_name = 'demo_last_activity'

insert_data_to_mysql(csv_file, db_config, table_name)