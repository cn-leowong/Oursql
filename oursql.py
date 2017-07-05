#coding:utf-8
#python_version : python2.7
#author:leo

import sys
import os
import time
import json
import hashlib
import argparse
from sql import *
from user import *


reload(sys)
sys.setdefaultencoding('utf-8')

db_filename = sys.argv[0]
db_dirname = os.path.dirname(db_filename)
db_abspath = os.path.abspath(db_dirname)

sql=''# the sql exec
current_db=''
db_path=db_abspath+'\data\\'
current_user=''


def setcurrent_db(name):
    global current_db
    current_db=name

def setcurrent_user(name):
    global current_user
    current_user=name

def  getcurrent_user():
    global current_user
    return current_user

class oursql(object):
    def __init__(self):
        self.description='''
* * * * * * * * * * * * * * * * * * * * * *
*     ___             ____   ___  _       *
*    / _ \ _   _ _ __/ ___| / _ \| |      *
*   | | | | | | | '__\___ \| | | | |      *
*   | |_| | |_| | |   ___) | |_| | |___   *
*    \___/ \__,_|_|  |____/ \__\_\_____|  *
*                                         *
*           version 2017-06               *
*           author   leo                  *
* * * * * * * * * * * * * * * * * * * * * *
        Welcome to use OurSQL!
'''
        self.loginwelcome='''
 ______     __  __     ______     ______     ______     __
/\  __ \   /\ \/\ \   /\  == \   /\  ___\   /\  __ \   /\ \\
\ \ \/\ \  \ \ \_\ \  \ \  __<   \ \___  \  \ \ \/\_\  \ \ \____
 \ \_____\  \ \_____\  \ \_\ \_\  \/\_____\  \ \___\_\  \ \_____\\
  \/_____/   \/_____/   \/_/ /_/   \/_____/   \/___/_/   \/_____/\n
'''
        self.help='''
Usage:\n
   -h
   -u <username>  -p <password>

   Default account: root 123456
   Default account: guest 123456

    1. show databases;
    2. create database <database>;
    3. drop database <database>;
    4. use <database>;
    5. help database;
    6. help
    7. exit

   Do these actions you should choose a database first:

    1. show tables;
    2. create table <table> (<column1> <data_type> <constraints>[,<c2> <d_t> <c>...]);
    3. insert into <table> (<column1>[,<c2>...]) values ((<v1>[,<v2>]...);
    4. delete from <table> where <condition>;
    5. update <table> set <column_name>=<val>[,c_n2=c_v2]... where <condition>;
    6. select [*|columns] from <table> [where <condition>];
    7. help table <table>;

   Do these actions you should choose the database oursql:
   
    1. grant <action> on <database> to <username>;
    2. revoke  <action> on <database> from <username>;
'''

    def welcome(self):
        '''
        welcome information
        '''
        print(self.description)
        exit(0)
    def args(self):
        '''
        resolve the args
        '''
        parser = argparse.ArgumentParser(self.description)
        parser.add_argument('-u',nargs = '?',help='please put in your name the default is root')
        parser.add_argument('-p',nargs = '?',help='please put in your password')
        args = parser.parse_args()
        return args
    def md5encode(self,password):
        '''
        md5encode
        '''
        md5=hashlib.md5()
        md5.update(password)
        return md5.hexdigest()
    def login(self):
        '''
        login
        '''
        global current_user
        self.username=self.args().u
        self.password=self.args().p
        self.check_login(self.username,self.password)
    #    print flag
        if self.flag == -1:
            print('No such user\n')
            print('Please login again')
            exit(0)
        elif self.flag == 0:
            print('Username or password is wrong\n')
            print('Please login again')
            exit(0)
        elif self.flag == 1:
            print('Login Success!\n')
            current_user=self.username
            print self.loginwelcome
            self.login_success()
    def check_login(self,username,password):
        '''
        check login innformation
        '''
        global db_path
        with open(db_path+'\oursql.json', 'r') as f: #look out the json read
            infos = json.loads(f.read())
            self.flag=-1
            for info in infos['user']['data']:
                if username == info['username']:
                    md5=self.md5encode(password)
                    if md5==info['password']:
                        self.flag=1
                        break
                    else:
                        self.flag=0
                        break

    def login_success(self):
        '''
        after login success you can input your sql
        '''
        global current_db
        global sql# look out the global variables
        if current_db is '':
            sql=raw_input('OurSQL> ')
        else:
            sql=raw_input('OurSQL['+current_db+']> ')
        if sql == 'quit' or sql == 'exit':  #exit
            print('Bye')
            time.sleep(1)
            exit(0)
        elif sql == 'help' or sql == '?': # the help information
            print(self.help)
            self.login_success() #  this is a nesting  look out!
        elif sql == '':
            print(self.help)
            self.login_success() #  this is a nesting  look out!
        else:
            #self.query(sql)
            #self.login_success()
            while(1):
                if sql[-1] is not ';':#Support multiline input
                    sql=sql+' '+raw_input('            >')
                else:
                    break

if __name__=='__main__':
    oursql=oursql()    #create the object
    if len(sys.argv)==1:
        oursql.welcome()   #show the help information
    oursql.login()        #show the welcome and login
    sqlobject=Sql(sql,current_user) #create the object
    sqlobject.query()
    current_db=get_current_db_sql()
    del sqlobject  #del the object
    while (1):
        oursql.login_success()
        sqlobject=Sql(sql,current_user) #create other object
        sqlobject.query()
        current_db=get_current_db_sql()
        del sqlobject  #del the object
