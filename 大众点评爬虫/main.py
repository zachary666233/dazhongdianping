# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:42:52 2018
Devised on 3.7, 2018

@original_author: bin
@author: 朱钟炜

注意事项：
1.svg，css文件会变更；目前需要手动变更；parse的文件也需要变更
2.cookies需要手动变更-评论页面；用户页面
"""

#目标爬取店铺的评论

import requests
from bs4 import BeautifulSoup
import time, random
import mysqls
from parse_svg import *
import re
from fake_useragent import UserAgent
import os



#载入加密的scg和css文件
font_url='http://s3plus.sankuai.com/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/1f1a32c9b1afbc379de928145deb65b5.svg'
css_url = 'http://s3plus.sankuai.com/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/9869b0360aada9913890f8e0c784ef21.css'
font_dict=build_font_dict(font_url)
css_dict=build_css_dict(css_url)
print('解析词典载入成功')

#随机请求头
ua = UserAgent()

#设置cookies
with open(r'Cookies.txt','r') as o:
    cookies = [x.strip() for x in o.read().split('\n')]

#设置refers
with open(r'Refers.txt','r') as o:
    refers = [x.strip() for x in o.read().split('\n')]

# #从ip代理池中随机获取ip
ips = open('proxies.txt','r').read().split('\n')

def get_random_ip():
   ip = random.choice(ips)
   pxs = {ip.split(':')[0]:ip}
   return pxs

#获取html页面
def getHTMLText(url,code="utf-8"):
    headers = {
        'User-Agent': ua.random,
        'Cookie': cookies[0],
        'Proxy-Connection': 'keep-alive',
        'Host': 'www.dianping.com',
        'Referer': random.choice(refers)}
    try:
        time.sleep(random.random()*6 + random.randint(2,6))
        r=requests.get(url, timeout = 5, headers=headers,
                      proxies=get_random_ip()
                       )
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        print("产生异常")
        return "产生异常"

#因为评论中带有emoji表情，是4个字符长度的，mysql数据库不支持4个字符长度，因此要进行过滤
def remove_emoji(text):
    try:
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'',text)

#解析用户信息
def parse_cus(url):
    '''通过链接的href解析得到用户的性别、地区
    部分用户无性别属性'''
    html = requests.get(url,headers = {
        'User-Agent': ua.random,
        'Cookie': cookies[1],
        'Proxy-Connection': 'keep-alive',
        'Host': 'www.dianping.com',
        }).text
    soup = BeautifulSoup(html,"lxml")
    info = soup.find('span',class_='user-groun')
    try:
        sex = info.i['class'][0]
    except:
        sex = '无'
    try:
        location = info.text
    except:
        location = '无'
    if sex=='无' and location=='无':
        print('警告：可能需要更改cookies')
    return sex,location

#解析加密文字
def parse_code(text):
    ''''''
    def transform(word):
        try:
            return tag_to_word(re.findall(r'".*?"', word)[0].replace('"', ''),
                               font_dict,
                               css_dict)
        except:
            return word
    text=re.sub(pattern=r"img alt.*?\.png\"",repl='',string=text)
    words = ''.join([transform(x) for x in re.split(r'>|<', text.replace('/svgmtsi', '')) if x != ''])
    return words

#从html中提起所需字段信息
def parsePage(html,shpoID):
    infoList = [] #用于存储提取后的信息，列表的每一项都是一个字典
    soup = BeautifulSoup(html, "html.parser")
    for item in soup('div','main-review'):
        cus_id = item.find('a','name').text.strip()
        try:
            cus_sex,cus_location = parse_cus('http://www.dianping.com{}'.format(item.a['href']))
        except:
            cus_sex, cus_location = '无','无'
        comment_time = item.find('span','time').text.strip()
        try:
            comment_star = item.find('span',re.compile('sml-rank-stars')).get('class')[1]
        except:
            comment_star = 'NAN'
        if '收起评论' in str(item.find('div', "review-words")):
            cus_comment = parse_code('\n'.join(str(item.find('div', "review-words")).split('\n')[1:-6]).strip()).replace('/img','')
        else:
            cus_comment = parse_code('\n'.join(str(item.find('div', "review-words")).split('\n')[1:]).replace('/div','').replace('/img','').strip())
        if 'svgmtsi' in cus_comment:
            print('警告：可能需要变更svg和css文件，并修改程序')
        scores = str(item.find('span','score'))
        try:
            kouwei = re.findall(r'口味：([\u4e00-\u9fa5]*)',scores)[0]
            huanjing = re.findall(r'环境：([\u4e00-\u9fa5]*)',scores)[0]
            fuwu = re.findall(r'服务：([\u4e00-\u9fa5]*)',scores)[0]
        except:
            kouwei = huanjing = fuwu = '无'
        try:
            pics_soup = item.find_all('li',class_='item')
            pic_urls = [pic_soup.img['data-big'] for pic_soup in pics_soup]
        except:
            pic_urls = ['无']


        infoList.append({'cus_id':cus_id,
                         'cus_location':cus_location,
                         'cus_sex':cus_sex,
                         'comment_time':comment_time,
                         'comment_star':comment_star,
                         'cus_comment':remove_emoji(cus_comment),
                         'kouwei':kouwei,
                         'huanjing':huanjing,
                         'fuwu':fuwu,
                         'shopID':shpoID,
                         'pic_urls':pic_urls})
    return infoList

#构造每一页的url，并且对爬取的信息进行存储
def getCommentinfo(shop_url, shpoID, page_begin, page_end):
    for i in range(page_begin, page_end):
        try:
            url = shop_url + '/review_all/p' + str(i)
            html = getHTMLText(url)
            infoList = parsePage(html,shpoID)
            print('成功爬取第{}页数据,有评论{}条'.format(i,len(infoList)))
            for info in infoList:
                mysqls.save_data(info)
            #断点续传中的断点
            if (html != "产生异常") and (len(infoList) != 0):
                with open('xuchuan.txt','a') as file:
                    duandian = str(i)+'\n'
                    file.write(duandian)
            else:
                print('休息30-60s...')
                time.sleep(random.randint(30,60))
        except:
            print('跳过本次')
            continue
    return

getCommentinfo('http://www.dianping.com/shop/24606542',24606542, 35,100)

def xuchuan():
    if os.path.exists('xuchuan.txt'):
        file = open('xuchuan.txt','r')
        nowpage = int(file.readlines()[-1])
        file.close()
    else:
        nowpage = 0
    return nowpage

# #根据店铺id，店铺页码进行爬取
# # def craw_comment(shopID='521698',page = 53):
# #     shop_url = "http://www.dianping.com/shop/" + shopID + "/review_all/"
# #     #读取断点续传中的续传断点
# #     nowpage = xuchuan()
#     getCommentinfo(shop_url, shopID, page_begin=nowpage+1, page_end=page+1)
#     mysqls.close_sql()
#     return
#
# if __name__ == "__main__":
#     craw_comment()
        