#!/usr/bin/env python
#-*- coding: utf-8 -*-

import MySQLdb

conn = ''
cur = ''

def conn_db():
    conn = MySQLdb.connect(
            host = 'localhost',
            user = 'root',
            #passwd = passwd,
            db = 'test',
            port = 3306,
            )
    return conn

def create_cur():
    global conn
    conn = conn_db()
    return conn.cursor()

def execute_sql(sqlStr):
    global cur
    cur = create_cur()
    cur.execute(sqlStr)

def create_table():
    sqlStr = 'create table test_miao(id int, name varchar(20), surname varchar(10))'
    execute_sql(sqlStr)

def insert_data(*arg):
    print arg
    sqlStr = 'insert into test_miao values("%s", "%s", "%s")' % (arg[0], arg[1], arg[2])
    print sqlStr
    execute_sql(sqlStr)
    conn.commit()

def query_data():
    print 'All data in test_miao table:'
    sqlStr = 'select * from test_miao'
    execute_sql(sqlStr)
    res = cur.fetchall()
    for i in res:
        print i

def main():
    #create_table()
    #insert_data()
    query_data()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
