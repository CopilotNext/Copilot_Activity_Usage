## Update Notes

- [Feature] Added new feature X
- [Bug Fix] Fixed issue with Y
- [Improvement] Improved performance of Z


## Update Notes in 2023/9/1

- [Feature] 修改项目结构，所有的数据保存在data目录下，所有的图片保存在static目录下；
- [Bug Fix] Fixed issue with Y
- [Improvement] Improved performance of Z

| Previous Name | New Name | Comments |
| --- | --- | --- |
| activity_processed.csv | {org}_activity.csv |  |
| activity_processed_split.csv |{org}_activity_details.csv  |  |
|{now}.csv  |{org}_{now}.csv  |  |
|{now}_processed.csv  |{org}_{now}_active.csv  |  |
|{now}_processed.csv  |{org}_{now}_active_details.csv  |  |
|new added    |{org}_last_activity.csv  | 保存最近一次获取last activity的结果，以便产生最新的报告 |

## Update Notes in 2023/9/2

- [Feature] 把active_activity，以及activity_activity_details的数据保存在SQLites数据库中，以提高效率并方便后续读取

## Update Notes in 2023/9/4

- [Feature] 产生更多类型的报表，分别是针对last_activity的，以及针对activit_active_details的
- [Bug Fix] Fixed issue with Y
- [Improvement] Improved performance of Z


| 报表名字  | 内容 | Comments |
| --- | --- | --- |
| {org}_Last_Activity_usage.png| 分配后，从未登录使用过Copilot的用户 | 针对last_activity |
| activity_processed_split.csv |最近7天未试用过Copilot的用户  |  针对last_activity |
|柱状图-最近30天按照使用频率排序 |{org}_{now}.csv  |  |
|饼状图--最近30天按照开发工具显示  |{org}_{now}_active.csv  |  |
|饼状图---最近30天按照Copilot Feature 显示  |{org}_{now}_active_details.csv  |  |
|{self.org}_daily_active_users.png |TBD-按照天排列的每天使用量（每用户每天只一次）|散点图 |

## Update Notes in 2023/9/7

- [Feature] 重新设计界面，完成初始化V1版本；

## Update Notes in 2023/9/11

- [Feature] 在data目录和static目录下，都增加一层目录，目录名是{org};从而更好更好的管理资源
- [Feature] 自动化Job中，只实现定时刷新的操作；把产生报表的操作转移到页面部分来完成；从而更好分开前后端
- [Feature] 同时，支持多个Org;从页面上可以切换Org (Draft)


- [Feature] 重新设计界面，完成初始化V1版本；

## Update Notes in 2023/9/13

- [Feature] 支持多Organization
- [Feature] 测试了EMU的场景；
- [Feature] 支持不同Organization,使用不同的Access Code


## Update Notes in 2023/9/15

- - [Bug Fix] 修改默认返回的seat数字，默认是1页，每页50个用户，修改为200个；url = f'https://api.github.com/orgs/{org}/copilot/billing/seats?per_page=200'


## Update Notes in 2023/9/25

- [Feature] 修改为从data/orgs.csv文件读取信息
- [Feature] 修改了删除，增加组织的操作，方便用户配置

## Update Notes in 2023/10/8

- [Feature] Add venv support for python project
- [Feature] use pip freeze to generate requirements.txt (update compitable between flask 3.0 and Werkzeug 3.0)
- [Feature] Add docker support for python flask project

## Update Notes in 2023/10/9
- [Bug Fix] fix bug that only 20 limit for access code in webapge
- [Feature] Add K8S support
- [Feature] Add More logs for debug, especially for jobs 

## Update Notes in 2023/10/10
- [Feature] Create both /data and /static folder when not exist
- [Feature] add a scheduler to run job every 6 hours in refresh_orgs_job.py
- [Feature] add Dockerfile-job to run job in docker container
- [Feature] Azure File Share support for app/data and app/static (both for App Service and Container App), it is referring to https://docs.microsoft.com/en-us/azure/app-service/configure-connect-to-azure-storage?pivots=container-linux#mount-file-share; and https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts?pivots=azure-portal

## Update Notes in 2023/10/11
- [Feature] update templates/index.html to be more friendly (remove go to main page , As itself is main page)
- [Feature] update templates/config.html to be use local /JS and /CSS files, instead of using online version, to save time for loading
- [Bug Fix] Set default organization to be the first one in orgs.csv, and set session to it. So that when user open the page, it will show the first organization's data

## Update Notes in 2023/10/24
- [Feature] upadte dockerignore to only allow data/orgs.csv and data/Demo; static/Demo;

## Update Notes in 2023/10/31
- [Feature] UI nice update for idex.html and last_activity.html
- [Feature] Add strict check when adding new org, only organizatio with copilot can be added
- [Bug Fix] send page and per_page to get_seats, to avoid only 100 seats returned before. it uses url = f'https://api.github.com/orgs/{org}/copilot/billing/seats?per_page={per_page}&page={page}'




