

"""
This is a Flask web application that displays seat usage data for different organizations. 
The app reads organization names from a CSV file and displays them on the homepage. 
Users can select an organization and view seat usage reports and charts. 
The app also has a configuration page where new organizations can be added. 
The app runs a background thread that periodically fetches the latest seat usage data from an API.
"""


import time
from flask import Flask, render_template, send_file,request, session
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import os
from threading import Thread

from activity_report import ActivityReport
from latest_activity_report import LastActivityReport
from orgs_manger import MySQLOrgsManager, CSVOrgsManager
from create_factory import Factory
from get_usage_fromGithub import GetUsage_FromGithub



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# to get the orgs info from orgs.csv, then call get_usage_fromGithub.py to get the usage info
orgs_manager = Factory.create_orgs_manager()
#orgs=orgs_manager.get_orgs()


 # 这里需要从data/organization.csv中读取组织名;并把组织名保存在orgs中,然后传递给index.html
# orgs = []
""" with open('data/organization.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        orgs.append(row[0]) """

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the homepage with a list of organizations and a form to select an organization.
    """
    # 每次重新获得orgs列表
    orgs = orgs_manager.get_orgs()
    
    # 增加一个判断，如果orgs为空，则提醒用户需要首先配置config页面，然后跳转到config页面
    if len(orgs) == 0:
        # 页面上，首先弹出一个提示框(alert)，提示用户需要首先配置config页面
        # 然后跳转到config页面
        return render_template('config.html', orgs=orgs)

        
    # 如果session中没有org，则默认选取orgs列表中的第一个元素
    # 如果是post请求，则从请求中获取org，并保存在session中
    org = session.get('org', orgs[0])
    if request.method == 'POST':
        # 首先判断是否有org参数
        if 'org' in request.form:
            org = request.form['org']
            session['org'] = org
    else:
        session['org'] = org
    print('orgs in Index now are :',orgs)
    print('Current Org is  :',org)
    # Render the HTML template with the bar and pie charts
    return render_template('index.html', orgs=orgs, selected_org=org)
   # return render_template('index.html', org=f'{org}')
    
@app.route('/set_org')
def set_org():
    """
    Sets the selected organization in the session.
    """
  #  org = request.args.get('org')
    # print(f'org is {request.args.get('org')}')
    # org=request.form['org']
    # session['org'] = org
    return 'org set successfully!'
    # 跳转到主页
    return index()
    

@app.route('/report')
def report():
    """
    Returns an HTML table displaying the first 10 rows of the most recently processed CSV file.
    """
    org= session.get("org")
    usagedb = Factory.create_usage_db(org)
    df = pd.DataFrame(usagedb.load_last_activity(), columns=['id', 'Login', 'Last Activity Date', 'Last Editor Used'])
    # print the column names
    #print(df.columns)
    df = df.sort_values(by='Last Activity Date', ascending=False)
    return render_template('report.html', tables=[df.head(10).iloc[:, 1:].to_html(classes='data',index=False)], titles=df.columns.values[1:])

@app.route('/active_report')
def active_report():
    """
    Displays the latest activity report for the selected organization.
    """
    # restruct to use ActivityReport class,instead of active_report
    org= session.get("org")
    # to call ActivityReport from activity_report.py;

    usagedb = Factory.create_usage_db(org)
    report = ActivityReport(org=f'{org}',usage_db=usagedb)
    columns = ['IDE', 'Copilot-Feature', 'Login']
    for column in columns:
        report.print_ide_usage(days=30, column=column)
        report.print_ide_usage(days=30, column=column,type='bar')
    ActivityReport.print_daily_active_users(report,days=30)
    
    return render_template('active_report.html', org=f'{org}')



@app.route('/Last_activity_report')
def Last_activity_report():
    """
    Displays the last activity report for the selected organization.
    """
    # 需要从session中读取org信息
    org= session.get("org")

    # Initialize UsageDB
    UsageDB = Factory.create_usage_db(org)
    # 创建ActivityReport对象
    report = LastActivityReport(org=f'{org}',usage_db=UsageDB)
    # 获取最行数，赋值给变量row_count
    row_count =report.row_count
    row_count_not_null = report.row_count_not_null
    # 获得从来没有登录过的用户
    login_null_data = report.print_null_last_activity()
    print(f'login_null_data of org {org} is :',login_null_data)
    #print(f'login_null_data of org {org} is :',login_null_data.count)

    #获取最近7天未使用的登录数据
    login_data = report.print_last_activity_over_days(days=7)
    #产生最新的图片
    report.print_active_user()
    # 如果行数超过20行，则只显示前20行
    if len(login_data) > 20:
        login_data = login_data.head(20)

    return render_template('last_activity_report.html', org=f'{org}',login_null_data=login_null_data,login_data=login_data,row_count=f'{row_count}', row_count_not_null=f'{row_count_not_null}')

@app.route('/config', methods=['GET', 'POST'])
@app.route('/Admin', methods=['GET', 'POST'])  # Add this line
def config():
    """
    Displays the configuration page where new organizations can be added.
    """
    # 如果是POST请求，则获取表单中的组织名
    if request.method == 'POST':
        org =request.form['org']
        # 将组织名写入配置文件
        org_name = request.form['org']
        access_code = request.form['access_code']
        retention_days = int(request.form['log_days'])
        frequence = int(request.form['Refresh_Frequence'])
        # 根据组织的名字和访问码，通过调用get_usage_byAPI.py中的get_copilot_by_org方法，检查该组织是否配置了Copilot;如果配置了，则返回用户信息，否则返回False
        try:
            result = GetUsage_FromGithub(org_name,access_code).get_copilot_by_org()
        except Exception as e:
            return f'<a href="/config">Go back to config page</a>  Error occurred when checking Copilot:,pls double check the organization name and access code {e}  '
        if not result:
            return f"<a href='/config'>Go back to config page</a> Access code doesn't match the  {org_name}.pls double check the access code for {org_name}"

        
        orgs_manager.add_org(org_name, access_code,frequence,retention_days=retention_days)
        # 创建组织的文件夹
        os.makedirs(f'static/{org}', exist_ok=True)
        os.makedirs(f'data/{org}', exist_ok=True)
       
        # Redirect to the config page
        # display a message to say the org was added successfully
        return f'Organization {org} added successfully! <a href="/config">Go back to config page</a> '
        #orgs = orgs_manager.get_orgs()
        #return render_template('config.html', orgs=orgs)
    else:
        # 读取配置文件中的组织名
        orgs = orgs_manager.get_orgs()
        # Render the HTML template with the list of organizations
        

        return render_template('config.html', orgs=orgs)

@app.route('/delete_org', methods=['POST'])
def delete_org():
    """
    Deletes the selected organization.
    """
    # org = request.args.get('org')
    org=request.form['org']
    print(f'org is going to be deleted {org}')
    # 删除组织的文件夹
    # os.rmdir(f'static/{org}')
    # os.rmdir(f'data/{org}')
    # 删除配置文件中的组织名
    orgs_manager.delete_org(org)
    return f'Organization {org} deleted successfully! <a href="/config">Go back to config page</a> '

@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    # 增加try,except,finally语句，以便在刷新数据的过程中，如果出现异常，也可以返回主页面
    try:
        print('Start to manually refresh Orgs at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )

    # 刷新获取最新的数据；update by zhuang on 2023/11/29
    # 仅仅刷新当前的org (以前是刷新整个orgs)
        # orgs_info = orgs_manager.get_orgs_info()
        # get_usage_byAPI.extract_copilot_by_orgs(orgs_info)
    
        org= session.get("org")
        # 获取当前org的信息，包括access_code等
        access_token = orgs_manager.get_org_access_code(org)
        if access_token is None:
            print(f'access_token is None,pls double check the access code for {org}')
            return f'<a href="/">Go back to the homepage</a> access_token is None,pls double check the access code for {org}'
        #access_token=org_info[0]
        # 调用load_save_Usage.py中的extract_copilot_by_orgs方法，获取当前org的最新数据
        # Get assignees
        #assignees = GetUsage_FromGithub(org, access_token).extract_copilot_by_org()

        # Initialize UsageDB
        UsageDB = Factory.create_usage_db(org)
        # call save_usage method to fetch data from github and save it to database or csv file
        UsageDB.save_usage()

     
        # 然后再针对当前选择中的org生成报告
        report = ActivityReport(org, UsageDB)
        #report = ActivityReport(org=f'{org}')
        columns = ['IDE', 'Copilot-Feature', 'Login']
        for column in columns:
            report.print_ide_usage(days=30, column=column)
            report.print_ide_usage(days=30, column=column,type='bar')
        report.print_daily_active_users(days=30)

        print('End of manually refresh Orgs at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )

        # 显示刷新成功; 并提供一个返回主页面的链接，以便用户可以返回主页面
        return f'Data refreshed successfully! <a href="/">Go back to the homepage</a>'
    except Exception as e:
        return f'<a href="/">Go back to the homepage</a> Error occurred when refreshing data:,pls double check the access code {e}'
@app.route('/migrate', methods=['GET', 'POST'])
def migrate():
    return render_template('migrate.html')

@app.route('/migrate_action')
def migrate_action():
    # call orgs_manager.migrate_from_csv to migrate orgs from csv to mysql
    orgs_manager.migrate_from_csv()
    # create orgs_manager from csv. then fetch orgs, for each org, migrate data from csv to mysql
    orgs_manager_csv = CSVOrgsManager('data/orgs.csv')
    orgs = orgs_manager_csv.get_orgs()
    for org in orgs:
        usagedb_migrate = Factory.create_usage_db(org)
        usagedb_migrate.migrate_from_csv()
    
    return f'migrate successfully! <a href="/">Go back to the homepage</a>'

def get_latest_data():
    """
    后台线程，每10分钟从API获取最新的座位使用数据。
    """
    
    while True:
        orgs_info = orgs_manager.get_orgs
        for  org in orgs_info:
            usagedb = Factory.create_usage_db(org)
            usagedb.save_usage()
        # 每10分钟刷新依次，这一个以后可以修改为从配置文件中读取；现在为了测试，暂时设置为10分钟
        #time.sleep(10 * 60)
        # 修改为每12个小时刷新一次， updated by zhuang 2023/9/27
        time.sleep(12 * 60 * 60)

if __name__ == '__main__':
    #启动job线程
    # job_thread = Thread(target=get_latest_data)
    # job_thread.start()
    #启动Flask应用
    app.run(debug=True)