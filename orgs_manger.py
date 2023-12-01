import csv
import os
import mysql.connector

class BaseOrgsManager:
    # file name is the name of the file that stores the orgs info. for example, orgs.csv
    # for non-csv file, the file name is the name of the table in the database, for example, orgs
    def __init__(self, filename='orgs'):
        self.filename = filename

    def add_org(self, Org_Name, Access_Code, refresh_frequency=60, retention_days=7):
        try:
            os.makedirs(f'data/{Org_Name}', exist_ok=True)
            os.makedirs(f'static/{Org_Name}', exist_ok=True)
        except Exception as e:
            print(f"Error in add_org: {e}")

    def delete_org(self, Org_Name):
        try:
            pass
        except Exception as e:
            print(f"Error in delete_org: {e}")

    def get_orgs(self):
        try:
            pass
        except Exception as e:
            print(f"Error in get_orgs: {e}")

    def get_org_Access_Code(self, Org_Name):
        try:
            pass
        except Exception as e:
            print(f"Error in get_org_Access_Code: {e}")
    # get orgs info from the file or database, the return value is a list of dict, each dict contains the org info. it includes Org_Name, Access_Code now
    def get_orgs_info(self):
        try:
            pass
        except Exception as e:
            print(f"Error in get_orgs_info: {e}")
    
class CSVOrgsManager(BaseOrgsManager):

    def __init__(self, filename='orgs'):
        super().__init__(filename)
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Org_Name', 'Access_Code', 'Refresh_Frequence', 'Retetion_Days'])

    def add_org(self, Org_Name, Access_Code, refresh_frequency=60, retention_days=7):
        try:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([Org_Name, Access_Code, refresh_frequency, retention_days])
            # need to create new folder for the org in future. static/Org_Name, and data/Org_Name
            super().add_org(Org_Name, Access_Code, refresh_frequency, retention_days)
        except Exception as e:
            print(f"Error in add_org: {e}")

    def delete_org(self, Org_Name):
        try:
            temp_filename = self.filename + '.temp'
            with open(self.filename, 'r', newline='') as csvfile, open(temp_filename, 'w', newline='') as temp_csvfile:
                reader = csv.reader(csvfile)
                writer = csv.writer(temp_csvfile)
                for row in reader:
                    if row[0] != Org_Name:
                        writer.writerow(row)
            os.remove(self.filename)
            os.rename(temp_filename, self.filename)
        except Exception as e:
            print(f"Error in delete_org: {e}")

    def get_orgs(self):
        try:
            orgs = []
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    orgs.append(row[0])
            return orgs
        except Exception as e:
            print(f"Error in get_orgs: {e}")

    def get_org_access_code(self, Org_Name):
        try:
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    if row[0] == Org_Name:
                        return row[1]
            return None
        except Exception as e:
            print(f"Error in get_org_Access_Code: {e}")

    def get_orgs_info(self):
        try:
            orgs_info = []
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    orgs_info.append([row[0],row[1]])
            return orgs_info
        except Exception as e:
            print(f"Error in get_orgs_info: {e}")
    
class MySQLOrgsManager(BaseOrgsManager):
    def __init__(self, connection, filename='orgs'):
        super().__init__(filename)
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {filename} (
                Org_Name VARCHAR(255) NOT NULL PRIMARY KEY,
                Access_Code VARCHAR(255) NOT NULL,
                Refresh_Frequence INT,
                Retetion_Days INT
            )
        ''')
        self.connection.commit()
    

    def add_org(self, Org_Name, Access_Code, refresh_frequency=60, retention_days=7):
        try:
            
            # insert into mysql orgs table
            sql = f"INSERT INTO {self.filename} (Org_Name, Access_Code, Refresh_Frequence, Retetion_Days) VALUES (%s, %s, %s, %s)"
            values = (Org_Name, Access_Code, refresh_frequency, retention_days)
            self.cursor.execute(sql, values)
            self.connection.commit()
            # call add_org from base class to create folders, for log and debug.
            super().add_org(Org_Name, Access_Code, refresh_frequency, retention_days)
        except Exception as e:
            print(f"Error in add_org: {e}")

    def delete_org(self, Org_Name):
        try:
            sql = f"DELETE FROM {self.filename} WHERE Org_Name = %s"
            self.cursor.execute(sql, (Org_Name,))
            self.connection.commit()
        except Exception as e:
            print(f"Error in delete_org: {e}")

    def get_orgs(self):
        try:
            sql = f"SELECT Org_Name FROM {self.filename}"
            self.cursor.execute(sql)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error in get_orgs: {e}")

    def get_org_access_code(self, Org_Name):
        try:
            sql = f"SELECT Access_Code FROM {self.filename} WHERE Org_Name = %s"
            self.cursor.execute(sql, (Org_Name,))
            result = self.cursor.fetchone()            
            return result[0] if result else None

        except Exception as e:
            print(f"Error in get_org_Access_Code: {e}")

    def get_orgs_info(self):
        try:
            sql = f"SELECT Org_Name, Access_Code FROM {self.filename}"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_orgs_info: {e}")

# 调用如上的代码，实现新增加一个org，orgname为demo01，Access_Code为ddd，刷新频率为60，保留天数为7;
# 传入参数，如果参数是csv,则使用CSVOrgsManager模式，如果是mysql，则使用MySQLOrgsManager模式
# 请以一个函数的形式实现，函数名为add_org

def test_org(Org_Name, Access_Code, refresh_frequency=60, retention_days=7, file_type='csv'):
    if file_type == 'csv':
        orgs_manager = CSVOrgsManager('data/orgs.csv')
    elif file_type == 'mysql':
        db_config = {'user': 'zhuang', 'password': 'copilotusage', 'host': 'localhost', 'database': 'copilot_usage'}
        orgs_manager = MySQLOrgsManager(mysql.connector.connect(**db_config), 'orgs')
                                        
    orgs_manager.add_org(Org_Name, Access_Code, refresh_frequency, retention_days)
    # 返回组织的访问码
    orgs_manager.get_org_Access_Code(Org_Name)
    print(orgs_manager.get_org_Access_Code(Org_Name))

    #删除一个组织
    orgs_manager.delete_org(Org_Name)


# test_org('demo01', 'ddd', refresh_frequency=60, retention_days=7, file_type='csv')

# test_org('demo02', 'ddd', refresh_frequency=60, retention_days=7, file_type='mysql')

