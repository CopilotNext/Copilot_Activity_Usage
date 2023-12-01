import csv
import mysql.connector
import requests
import datetime
import os
from dotenv import load_dotenv

from load_save_Usage import CSV_UsageDB,MySQL_UsageDB
from get_usage_fromGithub import GetUsage_FromGithub
from orgs_manger import MySQLOrgsManager, CSVOrgsManager

class Factory:
    env = os.getenv('ENV', 'development')
    load_dotenv(f'.env.{env}')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'csv')
    DATABASE_TYPE =DATABASE_TYPE.lower()

    @staticmethod
    def create_orgs_manager():
        if Factory.DATABASE_TYPE == 'csv':
            return CSVOrgsManager('data/orgs.csv')
        elif Factory.DATABASE_TYPE == 'mysql':
            db_config = {'user': 'zhuang', 'password': 'copilotusage', 'host': 'localhost', 'database': 'copilot_usage'}
            return MySQLOrgsManager(mysql.connector.connect(**db_config), 'orgs')

    @staticmethod
    def create_usage_db(org):
        if Factory.DATABASE_TYPE == 'csv':
            return CSV_UsageDB(org)
        else:
            DB_USER=os.getenv('DB_USER')
            DB_PASSWORD=os.getenv('DB_PASSWORD')
            DB_HOST=os.getenv('DB_HOST')
            DB_DATABASE=os.getenv('DB_DATABASE')
            #db_config = {'user': 'zhuang', 'password': 'copilotusage', 'host': 'localhost', 'database': 'copilot_usage'}
            db_config = {'user': DB_USER, 'password': DB_PASSWORD, 'host': DB_HOST, 'database': DB_DATABASE}
            connection = mysql.connector.connect(**db_config)
            return MySQL_UsageDB(org, connection)
        
