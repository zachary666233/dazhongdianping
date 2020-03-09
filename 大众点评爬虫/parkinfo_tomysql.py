import pymysql

db=pymysql.connect(host="localhost",user="root",database="urban_park_beijing",password="1995216",port=3306)
cursor = db.cursor()


with open(r'park_id.txt','r',encoding='utf-8') as o:
    a = [x.split('-') for x in o.read().split('\n')]
    b = [x[0] for x in a]
    c = [int(x[1]) for x in a]


for i in range(50):
    sql = '''INSERT INTO park_id(Park_name,Park_id) VALUES(%s,%s)'''
    value_tup = (b[i]
                 ,c[i]
                 )

    cursor.execute(sql,value_tup)
    db.commit()
db.close()