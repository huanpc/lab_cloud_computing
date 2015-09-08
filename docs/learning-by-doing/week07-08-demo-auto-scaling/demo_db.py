#!/usr/bin/env python

import constant

__author__ = 'huanpc'
import MySQLdb

def connect_database():
    db = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="autoscaling@secret",db="policydb")
    cur = db.cursor()
   # cur.execute(constant.SCHEMA)
    cur.execute('SELECT * from policies where app_uuid="'+'f5bfcbad-7daa-4317-97cc-e42ae46b6ad1'+'"')
    row = cur.fetchall()
    print(row[0])
def main():
    connect_database()

if __name__ == '__main__':
    main()
