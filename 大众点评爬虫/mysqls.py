# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 15:45:05 2018

@author: bin
"""

import pymysql


#连接MYSQL数据库
db = pymysql.connect(host="localhost",user="root",database="urban_park_beijing",password="1995216",port=3306 )
cursor = db.cursor()

#在数据库建表
def creat_table():
    cursor.execute("DROP TABLE IF EXISTS DZDP")
    sql = '''CREATE TABLE DZDP(
            cus_id varchar(100),
            cus_location varchar(30),
            cus_sex varchar(10),
            comment_time varchar(55),
            comment_star varchar(55),
            cus_comment text(5000),
            kouwei varchar(55),
            huanjing varchar(55),
            fuwu varchar(55),
            shopID varchar(55),
            pic_urls text(5000)
            );'''
    cursor.execute(sql)
    return

#存储爬取到的数据
def save_data(data_dict):
    sql = '''INSERT INTO DZDP(cus_id,cus_sex,cus_location,comment_time,comment_star,cus_comment,kouwei,huanjing,fuwu,shopID,pic_urls) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    value_tup = (data_dict['cus_id']
                 ,data_dict['cus_sex']
                 ,data_dict['cus_location']
                 ,data_dict['comment_time']
                 ,data_dict['comment_star']
                 ,data_dict['cus_comment']
                 ,data_dict['kouwei']
                 ,data_dict['huanjing']
                 ,data_dict['fuwu']
                 ,data_dict['shopID']
                 ,'\n'.join(data_dict['pic_urls'])
                 )
    try:
        cursor.execute(sql,value_tup)
        db.commit()
    except:
        print('数据库写入失败')
    return


#关闭数据库
def close_sql():
    db.close()

# creat_table()