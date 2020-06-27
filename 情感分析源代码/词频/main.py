# -*- coding: utf-8 -*-
import os
import re
import json
import jieba
import collections
import pandas as pd
from jieba import posseg as ps

jieba.load_userdict("mydict.txt")#加载自定义词典，以便分错新词

stoplist = open('stopword.txt',encoding='utf8').read().split('\n')#加载停止词


def WordFre(fname,dataframe):#文件名，表格结构

    words = []
    for row in dataframe.iterrows():#读取每一行
        text = re.sub(r'\n|\r|\t|\d+-\d+-\d+|.*@.*:','',str(row[1]['User_comment']))#读取content这一格
        seg_list = list(jieba.cut(text) )#分词
        for seg in seg_list: #处理长度小于2的词，停止词
            seg = re.sub(r' ','',seg)
            if len(seg)<2 or seg in stoplist:
                continue
            try:
                int(seg)#去掉数字
            except:
                words.append(seg)
    count = collections.Counter(words)#统计，Counter方法统计词语出现的次数，其输出格式为字典
    datas = list(count.items())#转成数组
    datas.sort(key= lambda ss:ss[1] , reverse=True)#排序（对datas中的第二维数据词频数进行排序）

    alls = []
    for d in datas:#解析数组里的数据为json格式
        jdata = {}
        if d[0] in stoplist:
            continue
        jdata['word'] = d[0]
        jdata['count'] = d[1]
        alls.append(jdata)
    pd.DataFrame(alls,columns=['word','count']).to_excel('词频_{}.xlsx'.format(fname),index= False)#导出为表格


def do_all():
    root = 'data/'

    for f in os.listdir(root):#读取目录下的表格
        file = root + f
        data= pd.read_excel(file)
        for da in data.groupby('sentiment'):#按照sentiment情感分析的结果分组进行词频统计
            name =da[0]
            WordFre(name,da[1])
        name = f.split('.')[0]
        WordFre(name, data)#计算全部的词频

do_all()