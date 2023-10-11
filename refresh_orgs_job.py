import schedule
import time
from last_activity_report import LastActivityReport
from orgs import OrgsManager
import get_usage_byAPI
import datetime


def job():

    print('Start to refresh orgs at ',datetime.datetime.now())
    orgs_manager = OrgsManager('data/orgs.csv')
    orgs_info = orgs_manager.get_orgs_info()
    if orgs_info:
        get_usage_byAPI.extract_copilot_by_orgs(orgs_info)
        print('Finish to refresh orgs at ',datetime.datetime.now())
    else:
        print('No orgs in orgs.csv')

# 每6小时刷新一次
schedule.every(6).hours.do(job)

# 测试时候每分钟刷新一次
# schedule.every(1).minutes.do(job)
# 测试验证完毕，在最终的extract_copilot_by_org中增加了try except的逻辑，保证程序不会因为某个org的token失效而停止运行


while True:
    schedule.run_pending()
    #print("it is running in while")
    time.sleep(10)