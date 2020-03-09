# 大众点评爬虫
### 爬虫目标：
本人用于*urban_greenspace_study*项目的城市公园数据获取；用户评论获取
### 爬虫编写基础：
爬虫的编写是在Zheng weibin (py-bin)的基础上改写的 https://github.com/py-bin 如有冒犯，请联系本人
### *相比于原作者的程序，增加以下几个功能：*
- 1.解析大众点评字体加密功能-函数已封装到parse_svg.py
- 2.增加图片地址爬取功能-已封装到main.py中；pic_crawl.py文件可用于在数据库中获取地址，并将图片写入本地
- 3.增加对评论用户性别、属地信息的获取-以封装到main.py  
demo数据见dzdp_demo数据.csv文件
