
import requests
import datetime


class GetUsage_FromGithub:
    def __init__(self, org, access_token,per_page=100):
        self.org = org
        self.access_token = access_token
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            self.per_page = 100
            print('Warning: per_page is not an integer between 1 and 100, per_page is set to 100')
        else:
            self.per_page = per_page
    # 需要设定page参数，以指定获取第几页的数据；默认page=1
    def get_copilot_by_org(self,page=1):
        # Set the API endpoint and headers,目的地址类似https://api.github.com/orgs/ORG/copilot/billing/seats
        #url = f'https://api.github.com/orgs/{self.org}/copilot/billing/seats?page=5&per_page=100'
        url = f'https://api.github.com/orgs/{self.org}/copilot/billing/seats?page={page}&per_page={self.per_page}'
        headers = {
        'Authorization': f'token {self.access_token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
        }
        try:
            # Send the GET request to the API endpoint
            response = requests.get(url, headers=headers)
            # 检查返回的response是否是200，如果不是200，就报错
            if response.status_code != 200:
                print(f'Org is: {self.org}')
                raise Exception(response.status_code, response.text)
                return None
        except:
            print(f'Error: get_copilot_by_org failed, org is {self.org},pls check your access_token')
            return None
        # Print the response
        print(f"response was got successfully for org: {self.org}； page is {page}； per_page is {self.per_page}")
        # 返回response
        return response.json()

    # To get all the assignees for the org, all pages need to be retrieved
    def extract_copilot_by_org(self):
        # 调用get_copilot_by_org函数，获得response
        try:
            data = self.get_copilot_by_org()
        except:
            print(f'Error: get_copilot_by_org failed, org is {self.org},pls check your access_token')
            return None

        # Check if the data is valid
        if data is None or 'total_seats' not in data or 'seats' not in data:
            print(f'Error: Invalid data - {data}')
            return None
        
        # Extract the total_seats value
        total_seats = data['total_seats']
        print(f'Total seats in {self.org} in {datetime.datetime.now().strftime("%Y%m%d%H%M")} is {total_seats}')


        assignees = []
        page = total_seats // self.per_page + (total_seats % self.per_page > 0)

        for i in range(1, page + 1):
            # get the pages
            data = self.get_copilot_by_org(page=i)

            # Extract the login and id values for each assignee
            for seat in data['seats']:
                id = seat['assignee']['id']
                login = seat['assignee']['login']
                last_activity_at = seat['last_activity_at']
                last_activity_editor = seat['last_activity_editor']
                assignees.append([id, login, last_activity_at, last_activity_editor])

        # 返回assignees列表
        print(f"assignees was got successfully for org: {self.org}； ")
        return assignees


