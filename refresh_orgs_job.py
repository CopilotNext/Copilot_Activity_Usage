import schedule
import time
from active_report import ActivityReport
from orgs import OrgsManager
import get_usage_byAPI
import datetime


def job():

    # 1. Fetch data from github
    print('Start to refresh orgs at ',datetime.datetime.now())
    orgs_manager = OrgsManager('data/orgs.csv')
    orgs_info = orgs_manager.get_orgs_info()
    if orgs_info:
        get_usage_byAPI.extract_copilot_by_orgs(orgs_info)
        print('Finish to refresh orgs at ',datetime.datetime.now())
    else:
        print('No orgs in orgs.csv')

    # 2. Generate report for each org
    
    print('Start to generate report at ',datetime.datetime.now())
    # need to fetch the first column of orgs_info. for orgs_info, it is an array, each element is an array with two elements
    # orgs_info = [['org1','access_code1'],['org2','access_code2']]
    # for org in orgs_info:
    #     print(org[0])
    orgs=orgs_manager.get_orgs('Org_Name')
    for  org in orgs:
        print(f'Generate report for {org} in {datetime.datetime.now()} backend job')
        report = ActivityReport(org=f'{org}')
        columns = ['IDE', 'Copilot-Feature', 'Login']
        for column in columns:
            report.print_ide_usage(days=30, column=column)
            report.print_ide_usage(days=30, column=column,type='bar')
        ActivityReport.print_daily_active_users(report,days=30)
        print(f'End of Generate report for {org} in {datetime.datetime.now()} backend job')
    
    print('Finish to generate report at ',datetime.datetime.now())

# 每6小时刷新一次
schedule.every(6).hours.do(job)

# 测试时候每分钟刷新一次
# schedule.every(1).minutes.do(job)
# 测试验证完毕，在最终的extract_copilot_by_org中增加了try except的逻辑，保证程序不会因为某个org的token失效而停止运行


while True:
    schedule.run_pending()
    #print("it is running in while")
    time.sleep(10)