# Oursql

> A simple DBMS coded by python stroed by json.


## Background

* Write this sample database management system in the second grade third term.

* Using Python language, useing JSON to store data.

* The project took a total of 5 days, because of the time and personal level, there are a lot of bug and unreasonable places.

* There will be time later to maintain the update.

## Help
```
   -h
   -u <username>  -p <password>
```
```
   Default account: root 123456
   Default account: guest 123456
```
    1. show databases;
    2. create database <database>;
    3. drop database <database>;
    4. use <database>;
    5. help database;
    6. help
    7. exit

  ###### Do these actions you should choose a database first:

    1. show tables;
    2. create table <table> (<column1> <data_type> <constraints>[,<c2> <d_t> <c>...]);
    3. insert into <table> (<column1>[,<c2>...]) values ((<v1>[,<v2>]...);
    4. delete from <table> where <condition>;
    5. update <table> set <column_name>=<val>[,c_n2=c_v2]... where <condition>;
    6. select [*|columns] from <table> [where <condition>];
    7. help table <table>;

  ###### Do these actions you should choose the database oursql:

    1. grant <action> on <database> to <username>;
    2. revoke  <action> on <database> from <username>;




## Bugs

1. create table
2. revoke grant  
3. view  index

> blog: [leo-blog.cn](http://www.leo-blog.cn)
> email: leo_infosec@foxmail.com
