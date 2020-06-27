
# -*- coding: utf-8 -*-
import requests
import re
import os
import time
import datetime
from bs4 import BeautifulSoup
import json
import math
import pandas as pd


def parseFromJson():
    ALL = []
    root = 'data/'
    for f in os.listdir(root):
        file = root + f

        data = open(file,encoding='utf8').read()
        data = json.loads(data)
        name = data['Hotel_Name']
        comments = data['Comment']
        all = []
        for com in comments.keys():
            temp = comments[com]
            # print(temp['User_comment'])
            s_date = temp['Cumment_time']
            if int(s_date.split('-')[0])<2015:#2015年以前的先删除
                continue
            if len(temp['User_comment']) < 10:  #筛选去除无效短评
                continue
            temp['name'] = name
            all.append(temp)
            ALL.append(temp)
        pd.DataFrame(all).to_excel('data1/{}.xlsx'.format(name),index=False)#生成每个酒店的表格
    pd.DataFrame(ALL).to_excel('酒店评论.xlsx',index=False)#生成所有数据的表格

parseFromJson()




#过程大致描述：
#1.运行 筛选.Py 对酒店数据进行解析，筛选出2015-02及之后的数据
#2.进行情感分析，得出积极\中性\消极的数据表
#3.根据2得到的情感数据表，进行分词，得到4个词频表
#4.根据3得到的词频表进行词云，得到词云图
