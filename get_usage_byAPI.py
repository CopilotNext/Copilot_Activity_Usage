import requests
import json
import csv
import datetime
import pandas as pd
import os

# Set the access token and organization name

#org = 'your-org'
#access_token = 'gph_,,,'

# headers = {
#     'Authorization': f'token {access_token}',
#     'Accept': 'application/vnd.github.v3+json',
#     'X-GitHub-Api-Version': '2022-11-28'
# }
# 提取当前时间到变量，以便后面使用
now = datetime.datetime.now()

# 写一个函数，根据org名字，获得这个org下所有分配copilot的信息
def get_copilot_by_org(org='YourOrgName',access_token='youraccesscode',page=1,per_page=100):
    # Set the API endpoint and headers,目的地址类似https://api.github.com/orgs/ORG/copilot/billing/seats
    #url = f'https://api.github.com/orgs/{org}/copilot/billing/seats?page=5&per_page=100'
    url = f'https://api.github.com/orgs/{org}/copilot/billing/seats?page={page}&per_page={per_page}'
    
    headers = {
    'Authorization': f'token {access_token}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
    }

    try:
        # Send the GET request to the API endpoint
        response = requests.get(url, headers=headers)

        # 检查返回的response是否是200，如果不是200，就报错
        if response.status_code != 200:
            print(f'Org is: {org}')
            raise Exception(response.status_code, response.text)
            return None
    except:
        print(f'Error: get_copilot_by_org failed, org is {org},pls check your access_token')
        return None
    # Print the response
    print(f"response was got successfully for org: {org}； page is {page}； per_page is {per_page}")
    # 返回response
    return response.json()


 # 分析get_copilot_by_org返回的response，获得所有分配copilot的id，username，last_activity_at，last_activity_editor
 # 并保存到一个csv文件中，csv文件的格式如下：
 # id,login,last_activity_at,last_activity_editor
 # 123456,bluefeng,2021-08-25T09:34:20+08:00,vscode
 # csv文件的名字orgname开头，后面跟上日期时间（到分钟级别），比如{orgname}_202108250933.csv

def extract_copilot_by_org(org, access_token, per_page=100):
    # 调用get_copilot_by_org函数，获得response
    try:
        data = get_copilot_by_org(org, access_token, page=1, per_page=per_page)
    except:
        print(f'Error: get_copilot_by_org failed, org is {org},pls check your access_token')
        return None

    # Check if the data is valid
    if data is None or 'total_seats' not in data or 'seats' not in data:
        print(f'Error: Invalid data - {data}')
        return None

    # 如果per_page不是1-100的整数,则per_page=100,并打印警告信息
    if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
        per_page = 100
        print('Warning: per_page is not an integer between 1 and 100, per_page is set to 100')

    # Extract the total_seats value
    total_seats = data['total_seats']
    print(f'Total seats in {org} in {datetime.datetime.now().strftime("%Y%m%d%H%M")} is {total_seats}')

    # 定义一个列表变量，用来保存所有的assignee
    assignees = []

    ''' 计算需要循环的次数
    这行Python代码是计算需要多少页来显示所有的座位。这里的total_seats是总座位数，per_page是每页显示的座位数。
    total_seats // per_page是使用整数除法计算可以完全显示的页数。
    (total_seats % per_page > 0)是检查是否有剩余的座位不能完全填满一页。如果有剩余的座位，这个表达式的结果是True，在Python中True可以被当作1来处理，所以这会在页数上加一。
    如果没有剩余的座位，这个表达式的结果是False，在Python中False可以被当作0来处理，所以这不会改变页数。
    所以，这行代码的结果是需要的总页数。    
    '''
    page = total_seats // per_page + (total_seats % per_page > 0)

    for i in range(1, page + 1):
        # 获取一页数据
        data = get_copilot_by_org(org, access_token, page=i, per_page=per_page)

        # Extract the login and id values for each assignee
        for seat in data['seats']:
            id = seat['assignee']['id']
            login = seat['assignee']['login']
            last_activity_at = seat['last_activity_at']
            last_activity_editor = seat['last_activity_editor']
            assignees.append([id, login, last_activity_at, last_activity_editor])

    # 调用write_assignees_to_csv函数，把assignees列表写入到csv文件中
    write_assignees_to_csv(assignees, org=org)

# 把列表assignees写入到csv文件中
# csv文件的名字{org}开头，后面跟上日期时间（到小时级别），比如{org}_202108250933.csv
# csv文件的格式如下：
# id,Login,Last Activity Date,Last Editor Used
# 123456,logname01,2021-08-25T09:34:20+08:00,vscode
def write_assignees_to_csv(assignees,org='YourOrgName'):
    # csv文件,保存在data/{org}目录下，即data目录下，对每个org建立一个单独的目录；然后CSV文件命名以org开头，后面跟上日期时间（到小时级别），比如{org}_202108250933.csv
    now=datetime.datetime.now()
    filename = 'data/' + f'{org}/{org}_' + now.strftime("%Y%m%d%H%M") + '.csv'
    # 判断data目录下是否有{org}目录，如果没有，就创建一个
    try:
        os.mkdir(f'data/{org}')
        os.mkdir(f'static/{org}')
    except FileExistsError:
        pass

    # 打开csv文件，写入assignees列表,然后保存
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
        for assignee in assignees:
            writer.writerow(assignee)
        file.flush()
        file.close()
    
    
    # 调用generate_last_csv，保存最近一次的数据到{org}_last_activity.csv，以便后续报表分析
    generate_last_csv(filename)
    # 调用generate_process_csv函数，产生一个新的csv文件，主要是删除掉Last Activity Date 是空的行；文件名是{org}_{now}_active.csv ，
    generate_process_csv(filename)

    # 调用merge_process_csv函数，把filename文件内容合并到{org}_active.csv文件中,以保存所有的使用记录到一个文件中
    merge_process_csv(filename[:-4] + '_active.csv')

    # 调用generate_details_bysplit函数，把filename文件的“Last Editor Used”列，分拆为“IDE”等4列，拆分后的文件名是filename后面加上-details
    generate_details_bysplit(filename[:-4] + '_active.csv')

    # 调用merge_process_csv函数，把filename文件内容合并到{org}_active_details.csv文件中，其内容和{org}_active.csv文件内容一样，只是把Last Editor used 列多了4列
    merge_process_split_csv(filename[:-4] + '_active_details.csv')

    # To-do:后续计划做一个导出功能，主要就是导出{org}_active_details.csv文件内容到excel文件中，然后可以对excel文件进行分析
    return None

def get_lastactivity_by_username(username,org='YourOrgName'):
    # Set the API endpoint and headers
    url = f'https://api.github.com/orgs/{org}/members/{username}/copilot'

    # Send the GET request to the API endpoint
    response = requests.get(url, headers=headers)
    # Print the response
    #print(response.json())

    # call extract_last_activity,并且把返回值赋值给last_activity_at和last_activity_editor
    last_activity_at, last_activity_editor = extract_last_activity(response)

    # 把login和last_activity_at和last_activity_editor写入到activity.csv文件中
   
    with open('activity.csv', 'a', newline='') as csvfile:
        fieldnames = ['login', 'last_activity_at', 'last_activity_editor']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 如果文件是空的，就写入header
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'login': username, 'last_activity_at': last_activity_at, 'last_activity_editor': last_activity_editor})
    return last_activity_at, last_activity_editor

def extract_last_activity(response):
    # data = json.loads(response)
    data=response.json()
    last_activity_at = data['last_activity_at']
    last_activity_editor = data['last_activity_editor']
    print(last_activity_at, last_activity_editor)
    return last_activity_at, last_activity_editor

def generate_last_csv(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f'{file_path} FileNotFoundError')
        return None
    # 保留id，login，last_activity_at，last_activity_editor列
    #df = df.drop(columns=['id'], axis=1)
    #df = df.dropna(subset=['Last Activity Date'])
    
    # print(df)
    # 把df写入csv文件，csv文件的名字是file_path 去掉csv后缀，然后 + '_active.csv'；请修改
     # 获取org的值，其格式是filename中data/和/之间的内容
    org = file_path[5:file_path.find('/', 5)]
    df.to_csv('data/'+ f'{org}/{org}_' + 'last_activity.csv', index=False)
    return df

def generate_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f'{file_path} FileNotFoundError')
        return None
    # 保留id，login，last_activity_at，last_activity_editor列
    #df = df.drop(columns=['id'], axis=1)
    df = df.dropna(subset=['Last Activity Date'])
    
    # print(df)
    # 把df写入csv文件，csv文件的名字是file_path 去掉csv后缀，然后 + '_active.csv'
    df.to_csv(file_path[:-4] + '_active.csv', index=False)
    return df

# 写一个函数，把传入的filename的内容，合并到f'data/{org}_activity.csv'文件中
# 合并时候，如果有重复的行，就不要合并
# 因为f'data/{org}_activity.csv'文件中已经有了header，所以不需要再写入header
# 如果f'data/{org}_activity.csv'文件是空的，就直接把传入的csv文件内容复制到f'data/{org}_activity.csv'文件中
# 如果f'data/{org}_activity.csv'文件不是空的，就把传入的csv文件内容合并到f'data/{org}_activity.csv'文件中


def merge_process_csv(filename):
    # 打开filename文件，读取内容
    try:
        df=pd.read_csv(filename)
    except FileNotFoundError:
        print(f'{filename} FileNotFoundError')
        return None
    # 获取org的值，其格式是filename中data/和/之间的内容
    org = filename[5:filename.find('/', 5)]
    # print('org:',org)
    # 打开{org}.csv文件，读取内容
    try:
        df2=pd.read_csv(f'data/{org}/{org}_activity.csv')
    except FileNotFoundError:
        df2=pd.DataFrame(columns=['id','Login', 'Last Activity Date', 'Last Editor Used'])
        df2.to_csv(f'data/{org}/{org}_activity.csv', index=False)
        #return None
    # 如果f'data/{org}_activity.csv'文件是空的，就直接把传入的csv文件内容复制到f'data/{org}_activity.csv'文件中
    if df2.empty:
        df.to_csv(f'data/{org}/{org}_activity.csv', index=False)
    # 如果f'data/{org}_activity.csv'文件不是空的，就把传入的csv文件内容合并到f'data/{org}_activity.csv'文件中
    else:
        # 把filename文件内容合并到f'data/{org}_activity.csv'文件中
        df3=pd.concat([df2,df])
        # 确保合并后的df3中没有重复的行，判断依据是login列和last_activity_at列组合在一起，如果有重复的行，则删除，确保只有一行
        df3.drop_duplicates(subset=['Login','Last Activity Date'],keep='first',inplace=True)
        
        df3.to_csv(f'data/{org}/{org}_activity.csv', index=False) 
    return None

def merge_process_split_csv(filename):
    # 打开filename文件，读取内容
    try:
        df=pd.read_csv(filename)
    except FileNotFoundError:
        print(f'{filename} FileNotFoundError')
        return None
    # 获取org name;
    org = filename[5:filename.find('/', 5)]
    # print('org:',org)
    try:
        df2=pd.read_csv(f'data/{org}/{org}_activity_details.csv')
    except FileNotFoundError:
        df2=pd.DataFrame(columns=['id', 'Login', 'Last Activity Date', 'IDE', 'IDE Version', 'Copilot-Feature', 'Copilot-Version'])
        df2.to_csv(f'data/{org}/{org}_activity_details.csv', index=False)
      
    # 如果f'data/{org}_activity.csv'文件是空的，就直接把传入的csv文件内容复制到f'data/{org}_activity.csv'文件中
    if df2.empty:
        df.to_csv(f'data/{org}/{org}_activity_details.csv', index=False)
    # 如果f'data/{org}_activity.csv'文件不是空的，就把传入的csv文件内容合并到f'data/{org}_activity.csv'文件中
    else:
        # 把filename文件内容合并到f'data/{org}_activity.csv'文件中
        df3=pd.concat([df2,df])
        # 确保合并后的df3中没有重复的行，判断依据是login列和last_activity_at列组合在一起，如果有重复的行，则删除，确保只有一行
        df3.drop_duplicates(subset=['Login','Last Activity Date'],keep='first',inplace=True)
        
        df3.to_csv(f'data/{org}/{org}_activity_details.csv', index=False) 

    return None
# 去除掉f'data/{org}_activity.csv'文件中的重复行
def remove_duplicate(filepath):
    # 打开f'data/{org}_activity.csv'文件，读取内容
    df=pd.read_csv(filepath)
    org = filepath[5:filepath.find('/', 5)]
    print('org:',org)
    # 确保合并后的df中没有重复的行，判断依据是login列和last_activity_at列组合在一起，如果有重复的行，则删除，确保只有一行
    df.drop_duplicates(subset=['Login','Last Activity Date'],keep='first',inplace=True)
    df.to_csv(f'data/{org}/{org}_activity.csv', index=False)
    return None

def generate_details_bysplit(csv_file,org='YourOrgName'):
    # 检查csv_file文件是否存在，如果不存在，则默认使用activity.csv文件
    # 如果文件存在，就使用csv_file文件

    if csv_file == '':
        csv_file = f'data/{org}/{org}_last_activity.csv'

    recent_activity=pd.read_csv(csv_file)
    # Print the first five rows of the DataFrame
    # print(recent_activity.head())

    
    # Split the Last Editor Used column into multiple columns based on the / separator
   # recent_activity['Last Editor Used'] = recent_activity['Last Editor Used'].astype(set)  
    last_editor_used_split = recent_activity['Last Editor Used'].str.split('/', expand=True)
                                              
    # Check the number of columns in the last_editor_used_split DataFrame
    # print(last_editor_used_split.shape)

    # Rename the columns
    last_editor_used_split.columns = ['IDE', 'IDE Version', 'Copilot-Feature', 'Copilot-Version']

    # Concatenate the original DataFrame with the new columns
    recent_activity = pd.concat([recent_activity, last_editor_used_split], axis=1)

    # Drop the Last Editor Used column
    recent_activity = recent_activity.drop('Last Editor Used', axis=1)

    # Print the resulting DataFrame
    # print(recent_activity)

    # Save the DataFrame to a new CSV file, named split.csv
    csv_file_name = csv_file[:-4] + '_details.csv'
    recent_activity.to_csv(csv_file_name, index=False)

# 新建一个函数，传入一个列表orgs,然后遍历该orgs中的org,依次调用extract_copilot_by_org函数；从而获得所有org的copilot信息
# 修改了extract_copilot_by_orgs函数，传入的参数是orgsinfo，是一个列表，列表中的每个元素是一个列表，包含org和access_token
def extract_copilot_by_orgs(orgs_info):
    # 从orgsinfo列表中，分别取出org和access_token
    orgs=[]
    access_token=[]
    for orginfo in orgs_info:
        orgs.append(orginfo[0])
        access_token.append(orginfo[1])
    
    # 遍历orgs列表，依次调用extract_copilot_by_org函数,每次需要传入org和access_token
    for i in range(len(access_token)):
        extract_copilot_by_org(orgs[i], access_token[i])

    # 如果同一个账号在多个org中都有管理员权限，则其一个access_token就适用多个organizations;
    # access_token=''
    # for i in range(len(orgs)):
    #     extract_copilot_by_org(orgs[i], access_token)
 
    return None

# 调用remove_duplicate函数，去除掉f'data/{org}_activity.csv'文件中的重复行
# 这个是一次性的，不需要每次调用extract_copilot_by_org函数的时候都调用
# remove_duplicate()

# 调用extract_copilot_by_org函数，每次调用都会把copilot的信息保存到csv文件中
# extract_copilot_by_org('YourOrgName','youraccesscode')

