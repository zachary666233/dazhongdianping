import pymysql
import pandas as pd
import requests
from multiprocessing import Pool
import os


#连接MYSQL数据库
db = pymysql.connect(host="localhost",user="root",database="urban_park_beijing",password="1995216",port=3306 )

#sql语句
shopid = 1768201  #输入shopid
sqlcmd="select * from dzdp where shopID={}".format(shopid)

#利用pandas 模块导入mysql数据
df=pd.read_sql(sqlcmd,db)
# print(df.shape[0])

#pic_url
urls=[url.split('\n') for url in df['pic_urls']]
# print(len(urls))

#写入文件
index_tuples=[]
for i in range(len(urls)):
    if urls[i]!=['']:
        index_tuples += [(i,j) for j in range(len(urls[i]))]

root = r'E:\\大众点评图片\\双秀公园'

def Crawl(index_tuple):
    '''写入文件'''
    try:
        with open('{}\\{}_{}.jpg'.format(root,index_tuple[0],index_tuple[1]),'wb') as o:
            o.write(requests.get(urls[index_tuple[0]][index_tuple[1]]).content)
    except:
        print(index_tuple)

#多线程
if  __name__== '__main__':
    n=10
    pool=Pool(n)
    pool.map(Crawl,index_tuples)