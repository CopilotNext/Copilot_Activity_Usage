import schedule
import time
#from active_report import ActivityReport
#from orgs import OrgsManager
#import get_usage_byAPI
from activity_report import ActivityReport
from create_factory import Factory
#from dotenv import load_dotenv
import datetime
#import os


def job():
    # 1. Fetch data from github
    print('Start to refresh orgs at ',datetime.datetime.now())
    #orgs_manager = OrgsManager('data/orgs.csv')
    orgs_manager = Factory.create_orgs_manager()
    orgs_info = orgs_manager.get_orgs_info()
    if orgs_info:
        for org in orgs_info:
            try:
                print(f'Get usage for {org[0]} in {datetime.datetime.now()} backend job')
                # Initialize UsageDB
                UsageDB = Factory.create_usage_db(org[0])
                # call save_usage method to fetch data from github and save it to database or csv file
                UsageDB.save_usage()
                print(f'End of Get usage for {org[0]} in {datetime.datetime.now()} backend job')
            except Exception as e:
                print(f'Error occurred while getting usage for {org[0]}: {str(e)}')
        print('Finish to refresh orgs at ',datetime.datetime.now())
    else:
        print('No orgs found')

    # 2. Generate report for each org
    
    print('Start to generate report at ',datetime.datetime.now())
    # need to fetch the first column of orgs_info. for orgs_info, it is an array, each element is an array with two elements
    # orgs_info = [['org1','access_code1'],['org2','access_code2']]
    # for org in orgs_info:
    #     print(org[0])
    orgs=orgs_manager.get_orgs()
    for  org in orgs:
        try:
            print(f'Generate report for {org} in {datetime.datetime.now()} backend job')
            UsageDB = Factory.create_usage_db(org)
            report = ActivityReport(org, UsageDB)
            #report = ActivityReport(org=f'{org}')
            columns = ['IDE', 'Copilot-Feature', 'Login']
            for column in columns:
                report.print_ide_usage(days=30, column=column)
                report.print_ide_usage(days=30, column=column,type='bar')
            report.print_daily_active_users(days=30)
            print(f'End of Generate report for {org} in {datetime.datetime.now()} backend job')
        except Exception as e:
            print(f'Error occurred while generating report for {org}: {str(e)}')
    
    print('Finish to generate report at ',datetime.datetime.now())

# fetch data from github every 6 hours
#schedule.every(6).hours.do(job)

# for test, fetch data from github every 1 minutes
schedule.every(1).minutes.do(job)
# 测试验证完毕，在最终的extract_copilot_by_org中增加了try except的逻辑，保证程序不会因为某个org的token失效而停止运行


while True:
    schedule.run_pending()
    #print("it is running backend ")
    time.sleep(10)