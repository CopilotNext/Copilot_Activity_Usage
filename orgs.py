import csv
# import fcntl
import os

class OrgsManager:
    def __init__(self, filename):
        self.filename = filename

    def add_org(self, org_name, access_code, refresh_frequency=60, retention_days=7):
        with open(self.filename, 'a', newline='') as csvfile:
           #fcntl.flock(csvfile, fcntl.LOCK_EX)
            writer = csv.writer(csvfile)
            writer.writerow([org_name, access_code, refresh_frequency, retention_days])
            #fcntl.flock(csvfile, fcntl.LOCK_UN)

    def delete_org(self, org_name):
        temp_filename = self.filename + '.temp'
        with open(self.filename, 'r', newline='') as csvfile, open(temp_filename, 'w', newline='') as temp_csvfile:
            #fcntl.flock(csvfile, fcntl.LOCK_EX)
            reader = csv.reader(csvfile)
            writer = csv.writer(temp_csvfile)
            for row in reader:
                if row[0] != org_name:
                    writer.writerow(row)
            #fcntl.flock(csvfile, fcntl.LOCK_UN)

        os.remove(self.filename)
        os.rename(temp_filename, self.filename)

    def get_orgs(self):
        orgs = []
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header row
            for row in reader:
                orgs.append(row[0])
        return orgs
    
    def get_orgs(self, column_name):
        column_index = None
        orgs = []
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # skip header row
            for i, name in enumerate(header):
                if name == column_name:
                    column_index = i
                    break
            if column_index is None:
                raise ValueError(f'Column "{column_name}" not found')
            for row in reader:
                orgs.append(row[column_index])
            print('orgs:',orgs)
        return orgs
    
    # 增加一个方法，根据组织名获取组织的访问码
    def get_org_access_code(self, org_name):
        access_code = None
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if row[0] == org_name:
                    access_code = row[1]
                    break
        return access_code
    
    # 增加一个方法，获得组织的组织名，Access_Code
    def get_orgs_info(self):
        orgs_info = []
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                orgs_info.append([row[0],row[1]])
        return orgs_info
# # 测试删除一个组织的方法
# orgs_manager = OrgsManager('data/orgs.csv')
# orgs = orgs_manager.get_orgs('Org_Name')
# print('orgs are :',orgs)
# orgs_manager.delete_org('ddd')
# # 增加一个组织
# orgs_manager.add_org('ddd', 'ddd', retention_days=7)



        