import json
from datetime import datetime
import requests

class Copilot_Usage_By_Org:
    def __init__(self, org, access_token):
        self.org = org
        access_token = access_token
        url = f'https://api.github.com/orgs/{org}/copilot/billing/seats?per_page=200'

        headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
        }

        # Send the GET request to the API endpoint
        # 根据当前的时间，生成一个文件名
        now = datetime.now()
        self.filename = 'data/' + f'{org}/{org}_' + now.strftime("%Y%m%d%H%M") + '.csv'
        print(f'filename is {self.filename}')
        response = requests.get(url, headers=headers)

        # 检查返回的response是否是200，如果不是200，就报错
        if response.status_code != 200:
            print(f'Org is: {org}')
            raise Exception(response.status_code, response.text)
            return None
        data = response.json()
        # Check if the data is valid
        if data is None or 'total_seats' not in data or 'seats' not in data:
            print(f'Error: Invalid data - {data}')
            return None

        # 分析response，获得所有分配copilot的id，username，last_activity_at，last_activity_editor
        # Extract the total_seats value
        self.total_seats = data['total_seats']
        print(f'Total seats in {org} in {datetime.now().strftime("%Y%m%d%H%M")} is {self.total_seats}')
        # 定义一个列表变量，用来保存所有的assignee
        assignees = []
        # Extract the login and id values for each assignee
        for seat in data['seats']:
            id = seat['assignee']['id']
            login = seat['assignee']['login']
            last_activity_at = seat['last_activity_at']
            last_activity_editor = seat['last_activity_editor']
            assignees.append([id, login, last_activity_at, last_activity_editor])
        # 将assignees列表变量赋值给self.assignees
        print(f'assignees is {assignees}')
        self.assignees = assignees    
        

    def save_to_blob(self, data, filename):
        # 将数据转换为字符串
        data_str = json.dumps(data)

        # 将数据保存到Blob中
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=filename)
        blob_client.upload_blob(data_str, overwrite=True)

    def run_task_and_save_to_blob(self, org, access_token):
        # 提取当前时间到变量，以便后面使用
        now = datetime.now()
        filename = 'data/' + f'{org}/{org}_' + now.strftime("%Y%m%d%H%M") + '.csv'

        # 获取返回值，返回值是json格式的文档，保存在变量data中
        data = self.extract_copilot_by_org(org, access_token)

        # 将数据保存到Blob中
        self.save_to_blob(data, filename)

    # 初始化class,并测试
