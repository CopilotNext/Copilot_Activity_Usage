

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
import csv

from active_report import ActivityReport
import get_usage_byAPI
from last_activity_report import LastActivityReport
from orgs import OrgsManager



app = Flask(__name__)
app.secret_key = 'your_secret_key'
orgs_manager = OrgsManager('data/orgs.csv')
orgs = orgs_manager.get_orgs('Org_Name')



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
    orgs = orgs_manager.get_orgs('Org_Name')
    print('orgs in Index are :',orgs)
    # 如果session中没有org，则默认选取orgs列表中的第一个元素
    org = session.get('org', orgs[0])
    # 如果是post请求，则从请求中获取org，并保存在session中
    if request.method == 'POST':
        # 首先判断是否有org参数
        if 'org' in request.form:
            org = request.form['org']
            session['org'] = org
    print('orgs in Index now are :',orgs)
    print('org in Index now is :',org)
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
    Returns an HTML table displaying the first 5 rows of the most recently processed CSV file.
    """
    org= session.get("org")
    # 读取csv文件并按照Last Activity Date字段排序
    df = pd.read_csv(f'data/{org}/{org}_activity_details.csv').sort_values(by='Last Activity Date', ascending=False)
    # 取排序后的前5行并生成报告
    return render_template('report.html', tables=[df.head().iloc[:, 1:].to_html(classes='data')], titles=df.columns.values[1:])

@app.route('/active_report')
def active_report():
    """
    Displays the latest activity report for the selected organization.
    """
    #然后再生成报告
    org= session.get("org")
    report = ActivityReport(org=f'{org}')
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
    print('org:',org)
    
    # 创建ActivityReport对象
    report = LastActivityReport(org=f'{org}')
    # 获取最行数，赋值给变量row_count
    row_count =report.row_count
    row_count_not_null = report.row_count_not_null
    # 获得从来没有登录过的用户
    login_null_data = report.print_null_last_activity()
    print(f'login_null_data of org {org} is :',login_null_data)
    print(f'login_null_data of org {org} is :',login_null_data.count)

    #获取最近7天未使用的登录数据
    login_data = report.print_last_activity_over_days(days=7)
    #产生最新的图片
    report.print_active_user()
    # 如果行数超过20行，则只显示前20行
    if len(login_data) > 20:
        login_data = login_data.head(20)

    return render_template('last_activity_report.html', org=f'{org}',login_null_data=login_null_data,login_data=login_data,row_count=f'{row_count}', row_count_not_null=f'{row_count_not_null}')

@app.route('/config', methods=['GET', 'POST'])
def config():
    """
    Displays the configuration page where new organizations can be added.
    """
    # 如果是POST请求，则获取表单中的组织名
    if request.method == 'POST':
        org =request.form['org']
        # 创建组织的文件夹
        os.makedirs(f'static/{org}', exist_ok=True)
        os.makedirs(f'data/{org}', exist_ok=True)
        # 将组织名写入配置文件
        org_name = request.form['org']
        access_code = request.form['access_code']
        retention_days = int(request.form['log_days'])
        frequence = int(request.form['Refresh_Frequence'])
        orgs_manager.add_org(org_name, access_code,frequence,retention_days=retention_days)
       
        # Redirect to the homepage
        orgs = orgs_manager.get_orgs('Org_Name')
        return render_template('index.html', orgs=orgs)
    else:
        # 读取配置文件中的组织名
        orgs = orgs_manager.get_orgs('Org_Name')
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
    return f'Organization {org} deleted successfully!'

import time
import get_usage_byAPI

def get_latest_data():
    """
    后台线程，每10分钟从API获取最新的座位使用数据。
    """
    
    while True:
        # 执行extract_copilot_by_org函数，每10分钟执行一次,不要使用import模式，直接调用module.function()的方式
        # 首先定期刷新数据
        # get_usage_byAPI.extract_copilot_by_org(org)
        # get_usage_byAPI.extract_copilot_by_orgs(['org1','org2'])
        # orgs=['Baozun-LSD','Lilith-Dislyte','wondershare-2023','qunar-org1']
        #orgs = orgs_manager.get_orgs('Org_Name')
        # 修改为获得orgs_info信息，其中包含了所有的org_name,access_code
        orgs_info = orgs_manager.get_orgs_info()
        get_usage_byAPI.extract_copilot_by_orgs(orgs_info)
      
        # 每10分钟刷新依次，这一个以后可以修改为从配置文件中读取；现在为了测试，暂时设置为10分钟

        time.sleep(10 * 60)

if __name__ == '__main__':
    #启动job线程
    job_thread = Thread(target=get_latest_data)
    job_thread.start()
    #启动Flask应用
    app.run(debug=True)