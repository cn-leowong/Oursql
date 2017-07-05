import os
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

db_filename = sys.argv[0]
db_dirname = os.path.dirname(db_filename)
db_abspath = os.path.abspath(db_dirname)

db_path=db_abspath+'\data\\oursql.json'


class User(object):

    def checkdatabase(self,username,dbname):
        with open(db_path,'r') as f:
            infos=json.loads(f.read())
            data=infos['user']['data']
            for i in data:
                if i['username'] == username:
                    if dbname in i['db']:
                        return 1
                    else:
                        return 0





    def checkaction(self,username,action):
        with open(db_path,'r') as f:
            infos=json.loads(f.read())
            data=infos['user']['data']
            for i in data:
                if i['username'] == username:
                    if action in i['action']:
                        return 1
                    else:
                        return 0
