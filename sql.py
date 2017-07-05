#!/usr/bin/python
#coding:utf-8
#author:leo

import os
import re
import json
import sys
from user import *
from oursql import *


reload(sys)
sys.setdefaultencoding('utf-8')

db_filename = sys.argv[0]
db_dirname = os.path.dirname(db_filename)
db_abspath = os.path.abspath(db_dirname)

db_path=db_abspath+'\data\\'


current_user_class=''
current_db_sql=''
global ori_sql#the original sql no arry

def get_current_db_sql():
    global current_db_sql
    return current_db_sql


class Sql(object):
    def __init__(self,sql,user):
        self.sql=sql
        global ori_sql
        global db_path
        global current_user_class
        ori_sql=sql.lower().strip()
        current_user_class=user
    def query(self):
        '''
        to split the sql to arry using split
        '''
        global ori_sql
        self.sql=self.sql[0:len(self.sql)-1]
        self.sql=self.sql.lower().strip().split(' ')
        self.execu(self.sql)

    def execu(self,sql_words):
        '''
        to exec the sql arry
        '''
        global ori_sql
        global current_db_sql
        global db_path
        global current_user_class
        sql=ori_sql
        #len<2 error
        if len(sql_words) < 2:
            print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[0]))
            return

        type = sql_words[0]
        # check actions
        userobjetct=User()
        if not userobjetct.checkaction(current_user_class,type):
            print('Permission denied\n')
            return

        if type == 'use':
            '''
            use [db];
            '''
            db = sql_words[1] + '.json'
            if db not in os.listdir(db_path):
                print('Unknown database ', sql_words[1])
            else:
                # check dbs
                if not userobjetct.checkdatabase(current_user_class,sql_words[1]):
                    print('Permission denied\n')
                    return
                current_db_sql = sql_words[1]
                print('Database changed\n')
                self.use_database()

        elif type == 'show':
            if sql_words[1] == 'databases':
                '''
                show databases;
                '''
                self.show_databases()
            elif sql_words[1] == 'tables':
                '''
                show tables;
                '''
                if not current_db_sql:
                    print('No database selected')
                else:
                    self.show_tables()
            else:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[1]))

        elif type == 'create':
            if sql_words[1] == 'database':
                '''
                create database [db];
                '''
                try:
                    self.create_database(sql_words[2])
                except:
                    print("Can't create database '%s'"%(sql_words[2]))
            elif sql_words[1] == 'table':
                '''
                create table [tablename](
                id int 2 1 1 0,
                name char 16 1 0 0);
                '''
                if not current_db_sql:
                    print('No database selected')
                else:
                    pattern = re.compile(r'^create\s+table\s+(.*?)\s*\(')
                    name=re.search(pattern, sql)
                    tablename = name.group(1)
                    pattern = re.compile(r'\((.*?)\s*\)')
                    columns=re.search(pattern, sql)
                    if not columns:
                        print('A table must have at least 1 column')
                    else:
                        columns = columns.group(1).split(',')
                        self.create_table(tablename, columns)
            else:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[1]))

        elif type == 'drop':
            if len(sql_words)<3:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[1]))
                return

            if sql_words[1] == 'database':
                '''
                drop database [db];
                '''
                try:
                    self.drop_database(sql_words[2])
                except:
                    print('can\'t remove your database')
            elif sql_words[1] == 'table':
                '''
                drop table [tablename];
                '''
                if not current_db_sql:
                    print('No database selected')
                else:
                    self.drop_table(sql_words[2])
            else:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[2]))

        elif type == 'insert':
            '''
            insert into [tablename] (id,name,password) values (4,'leo','test');
            '''
            if not current_db_sql:
                print('Please choose a database first')
            else:
                tablename = sql_words[2]
                pattern = re.compile(r'\((.*?)\)')
                columns = re.findall(pattern, sql)
                if not columns:
                    print('You have an error in your SQL syntax')
                else:
                    self.insert(tablename, columns)

        elif type == 'delete':
            '''
            delete from [tablename] where id=1;
            '''
            if not current_db_sql:
                print('Please choose a database first')
            else:
                tablename = sql_words[2]

                pattern = re.compile(r'where (.*?);$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'
                self.delete(tablename, condition)

        elif type == 'update':
            '''
            update [tablename] set   name='leo'   where id=1
            '''
            if not current_db_sql:
                print('Please choose a database first')
            else:
                tablename = sql_words[1]

                pattern = re.compile(r'where\s+(.*?);$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'

                pattern = r'set\s+(.*?)\s+where' if result else r'set (.*?);$'# pehaps there is no where
                pattern = re.compile(pattern)
                result = re.search(pattern, sql)
                if not result:
                    print('You have an error in your SQL syntax')
                    return
                else:
                    self.update(tablename, result.group(1).split(','), condition)

        elif type == 'select':
            '''
            select usernaeme from user where id=1;
            '''
            if len(sql_words) < 4:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1'%(sql_words[3]))
                return

            if not current_db_sql:
                print('Please choose a database first')
            else:
                tablename = sql_words[3]

                pattern = re.compile(r'select\s+(.*?)\s+from')
                result = re.search(pattern, sql)
                if not result:
                    print('You have an error in your SQL syntax')
                    return
                else:
                    columns = result.group(1)

                pattern = re.compile(r'where (.*?);$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'
                self.select(tablename, columns, condition)
        elif type == 'help':
            if sql_words[1] == 'database':
                '''
                help database;
                '''
                self.show_databases()
            elif sql_words[1] == 'table':
                '''
                help table [tablename];
                '''
                if not current_db_sql:
                    print('Please choose a database first')
                    return
                if len(sql_words)<3:
                    print('You have an error in your SQL syntax')
                else:
                    tbname=sql_words[2]
                    self.help_table(tbname)

        elif type == 'grant':
            '''
            grant <action> on <database> to <username>;
            '''
            if len(sql_words) < 6:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1')
                return
            if current_db_sql != 'oursql':
                print('You must choose the oursql database')
                return
            pattern = re.compile(r'grant\s+(.*?)\s+on\s+(.*?)\s+to\s+(.*?);$')
            result = re.findall(pattern, sql)
            if not result:
                print('You have an error in your SQL syntax')
                return
            action_name=result[0][0]
            db_name=result[0][1]
            user_name=result[0][2]
            self.grant_user(action_name,db_name,user_name)

        elif type == 'revoke':
            '''
            revoke  select on dbname from root;
            '''
            if len(sql_words) < 6:
                print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax to use near "%s" at line 1')
                return
            if current_db_sql != 'oursql':
                print('You must choose the oursql database')
                return
            pattern = re.compile(r'revoke\s+(.*?)\s+on\s+(.*?)\s+from\s+(.*?);$')
            result = re.findall(pattern, sql)
            if not result:
                print('You have an error in your SQL syntax')
                return
            action_name=result[0][0]
            db_name=result[0][1]
            user_name=result[0][2]
            self.revoke_user(action_name,db_name,user_name)


        else:
            print('You have an error in your SQL syntax; check the manual that corresponds to your OurSQL server version for the right syntax')



    def grant_user(self,action,db,user):
        #grant <action> on <db> to <username>;
        global current_db_sql
        global db_path
        infos = self.use_database()
        flag = 0
        column_name_1 = 'action'
        column_value_1 = action
        column_name_2 = 'db'
        column_value_2 = db
        condition="data['username']=="+"'"+str(user)+"'"
        for data in infos['user']['data']:
            if eval(condition):
                flag += 1
                if (column_value_1 in data[column_name_1]) or (column_value_2 in data[column_name_2]):
                    print('You already have this permission')
                    return
                data[column_name_1]+= ','+column_value_1
                data[column_name_2]+= ','+column_value_2

        with open(db_path+current_db_sql+'.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            print('Query OK, %d row(s) affected' % flag)
    def revoke_user(self,action,db,user):
        #grant <action> on <db> from <username>;
        global current_db_sql
        global db_path
        infos = self.use_database()
        flag = 0
        column_name_1 = 'action'
        column_value_1 = action
        column_name_2 = 'db'
        column_value_2 = db
        condition="data['username']=="+"'"+str(user)+"'"
        for data in infos['user']['data']:
            if eval(condition):
                flag += 1
                if (column_value_1 not in data[column_name_1]) or (column_value_2 not in data[column_name_2]):
                    print('You don\'t have this permission')
                    return
                data[column_name_1] = data[column_name_1].replace(column_value_1,'')
                data[column_name_2] = data[column_name_2].replace(column_value_2,'')


        with open(db_path+current_db_sql+'.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            print('Query OK, %d row(s) affected' % flag)

    def show_databases(self):
        global db_path
        print('All databases:')
        for db in os.listdir(db_path):#listdir
            print('[*] ' + db[:-5])
        print('\r')

    def help_table(self,name):
        infos=self.use_database()
        if name not in infos.keys():
            print('Don\'t have this table')
        else:
            print infos[name]['column_proterty']

    def use_database(self):
        global current_db_sql
        global db_path
        dbname = db_path + current_db_sql + '.json'
        with open(dbname, 'r') as db:
            infos = db.read()
            infos = {} if not infos else json.loads(infos)
            return infos


    def create_database(self, dbname):
        global db_path
        db = db_path + dbname + '.json'
        if dbname+'.json' in os.listdir(db_path):
            print('Database exists')
        else:
            open(db, 'w')# rember try and except
            print('Database created')


    def drop_database(self, dbname):
        global db_path
        if not dbname+'.json' in os.listdir(db_path):
            print('Database does not exists')
        elif dbname==current_db_sql:
            print('Can\'t remove your database when you are using it')
        else:
            os.remove(db_path+dbname+'.json')#os.remove
            print('Database'+dbname+'is droped')


    def show_tables(self):
        infos = self.use_database()
        print('All tables:')
        if not infos:
            print('This database is empty')
        else:
            for info in infos:
                print('* ' + info)
        print('\r')


    def create_table(self, tablename, columns):
        global current_db_sql
        global db_path
        infos = self.use_database()
        if tablename in infos.keys():#keys()
            print('Table exists')
            return
        else:
            infos[tablename] = {}
            infos[tablename]['data'] = []
            infos[tablename]['primary_key'] = self.record_tableinfo(infos[tablename], columns)
            with open(db_path+current_db_sql+'.json', 'w') as f:
                infos = json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))#4 spaces
            print('Table created')

    def record_tableinfo(self, infos, columns):
        global current_db_sql
        global db_path
        infos['column_proterty'] = {}
        l = ['data_type', 'data_length', 'is_null', 'is_primary', 'is_foreign']
        primary_key = ''
        for column in columns:
            column_proterty = column.strip().split(' ')
            infos['column_proterty'][column_proterty[0]] = dict(zip(l, column_proterty[1:]))#pay attention to this zip and dict
            if infos['column_proterty'][column_proterty[0]]['is_primary'] == '1':
                primary_key = column_proterty[0]

        with open(db_path+current_db_sql+'.json', 'w') as f:
            infos = json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        return primary_key


    def drop_table(self, tablename):
        global current_db_sql
        global db_path
        infos = self.use_database()
        del infos[tablename]
        with open(db_path+current_db_sql+'.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))#using edit replace the drop
        print('Table is droped')

    def insert(self, tablename, columns):
        global current_db_sql
        global db_path
        infos = self.use_database()
        if tablename not in infos.keys():
            print('Table does not exists')
            return
        else:
            column_names = columns[0].split(',')
            #column_values = list(map(lambda x: x.strip(), columns[1].split(',')))
            column_values=columns[1].split(',')
            #for column_value in column_values:
                #column_value = column_value.split(' ')

            if not len(column_names) == len(column_values):
                print('Unknown column')
                return

            else:
                insert_data = dict(zip(column_names, column_values))
                if not self.is_primary(infos[tablename], insert_data):
                    print(infos[tablename]['primary_key'].upper(), 'is primary key')
                    return
                else:
                    if not infos[tablename]['column_proterty'].keys() == insert_data.keys():
                        print('Unknown column')
                        return
                    infos[tablename]['data'].append(insert_data)
            with open(db_path+current_db_sql+'.json', 'w') as f:
                infos = json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Query OK, %d row(s) affected' % len(column_values))


    def is_primary(self, infos, columns):
        primary_key = infos['primary_key']
        for info in infos['data']:
            if info[primary_key] == columns[primary_key]:
                return False
        return True


    def get_condition(self, string):
        pattern = re.compile(r'([a-z0-9]+)(.*?)([a-z0-9]+)')
        result = re.search(pattern, string)

        column_name = result.group(1)
        opration = '==' if result.group(2).strip() == '=' else result.group(2).strip()
        column_value = result.group(3)
        return "data['"+column_name+"']" + opration + "'"+column_value+"'"

    def where(self, string):
        if 'and' in string:
            string = string.split('and')
            string = list(map(self.get_condition, string))
            condition = string[0] + ' and ' + string[1]
        elif 'or' in string:
            string = string.split('or')
            string = list(map(self.get_condition, string))
            condition = string[0] + ' or ' + string[1]
        else:
            condition = self.get_condition(string)
        return condition

    def delete(self, tablename, condition):
        global current_db_sql
        global db_path
        infos = self.use_database()
        if not infos:
            print('This table is empty')
            return
        else:
            if tablename not in infos.keys():
                print('Table does not exists')
                return

            datas = infos[tablename]['data']
            try:
                remove_data = [data for data in datas if eval(condition)]# eval exec the code  for "where"
            except:
                print('Maybe your command is wrong, check where <...>')
                return

            for r in remove_data:
                infos[tablename]['data'].remove(r)#remove(r)
            with open(db_path+current_db_sql+'.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Query OK, %d row(s) affected' % len(remove_data))

    def update(self, tablename, columns, condition):
        global current_db_sql
        global db_path
        infos = self.use_database()
        if not infos:
            print('This table is empty')
            return
        else:
            if tablename not in infos.keys():
                print('Table does not exists')
                return

            flag = 0
            for column in columns:
                column = column.strip().split('=')
                column_name = column[0]
                column_value = column[1]
                if not column_name in infos[tablename]['column_proterty'].keys():
                    print('Unknown column', column_name)
                    return

                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            flag += 1
                            data[column_name] = column_value
                    except:
                        print('Maybe your command is wrong, check where <...>')
                        return
                if not flag:
                    print('Query OK, 0 row affected')
                    return

            with open(db_path+current_db_sql+'.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            print('Query OK, %d row(s) affected' % flag)

    def select(self, tablename, columns, condition):
        infos = self.use_database()
        if tablename not in infos.keys():
            print('Table does not exists')
            return

        if not infos:
            print('This table is empty')
            return
        else:
            if columns == '*':
                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            for key in sorted(data.keys()):
                                print(key+':', data[key])
                            print('\r')
                    except:
                        print('Maybe your command is wrong, check where <...>')
                        return
            else:
                columns = list(map(lambda x: x.strip(), columns.split(',')))#look out
                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            for column in columns:
                                if column not in data.keys():
                                    print('Unknown column')
                                    return
                                else:
                                    print(column+':', data[column])
                            print('\r')
                    except:
                        print('Maybe your command is wrong, check where <...>')
                        return
            print('Query OK!')
