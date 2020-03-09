import requests
from bs4 import BeautifulSoup as bs
import re



'''大众点评的css和svg文件的地址会间隔一定周期刷新
   需要自动获取svg和css文件的地址
   目前只能手动输入这两个地址'''

#载入svg和css文件
def build_font_dict(font_url):
    '''svg文件'''
    svg=requests.get(font_url).text
    soup=bs(svg,'lxml')
    font_dict={}
    for row in soup.find_all('text'):
        y=row['y']
        fonts=row.text
        for i in range(len(fonts)):
            font_dict[(i+1,int(y))] = fonts[i]
    return font_dict


def build_css_dict(css_url):
    '''css文件'''
    svg=requests.get(css_url).text
    css_dict={}
    matchs=re.findall(r't.*?\}.',svg)
    for match in matchs:
        xy = re.findall(r'-.*?px',match)
        try:
            css_dict[match[:5]] = (int(float(xy[0].replace('px',''))*-1),int(float(xy[1].replace('px',''))*-1))
        except:
            continue
    return css_dict


def tag_to_word(tag,font_dict,css_dict):
    '''输入加密的属性值，解析得到文字'''
    xy=css_dict[tag]
    x=(xy[0]+14)/14
    y=xy[1]+23
    return font_dict[x,y]