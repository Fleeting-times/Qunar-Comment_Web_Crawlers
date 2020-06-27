# -*- coding: utf-8 -*-
import os
import random
import pandas as pd
from imageio import imread
from wordcloud import WordCloud,ImageColorGenerator


class wordcloudapi():
    def __init__(self):
        self.keyword = ''
        self.data = None

    #生成随机颜色函数
    def random_color_func(self,word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
        color = ["hsl(180,80%,30%)","hsl(200,80%,30%)","hsl(240,90%,20%)","hsl(0, 100%, 40%)","hsl(225, 100%, 60%)","hsl(330, 100%, 20%)"]
        return random.choice(color)

    #将list转成dict
    def list2dic(self,mylist):
        mydic={}
        for value in mylist:
            mydic[value[0]] =value[1]
        return mydic

    def run(self):
        background = None
        pic = imread('a.png')#底图
        font = 'simhei.ttf' #字体
        self.data["word"] = self.data["word"].astype('unicode')#读取表格中的词频并转成unicode
        color_func = ImageColorGenerator(background) if background else self.random_color_func #定义字体颜色
        wcd = WordCloud(font_path=font, background_color='white', width=1200, height=800, max_font_size=300, color_func=color_func, mask=pic,prefer_horizontal = 0.8,random_state=42)
        #调用WordCloud画图，参数定义依次是：字体，背景色，图的宽度，图的高度，图中字的最大字体，字体颜色，词云形状，
        #prefer_horizontal 默认值0.90，浮点数类型。表示在水平如果不合适，就旋转为垂直方向，水平放置的词数占0.9，
        #字旋转角度
        mydict= self.list2dic(list(self.data.values))
        wcd.generate_from_frequencies(mydict)#传入词频字典
        picname = 'result/词云_{}.png'.format(self.keyword)
        wcd.to_file(picname)


root = 'data/'
for f in os.listdir(root):  #输出指定文件下的所有文件和文件夹列表
    file = root + f
    data = pd.read_excel(file)[:150]    #调用排名为前150的词
    a = wordcloudapi()#调用API
    a.keyword = f.split('.')[0].split('_')[1]
    a.data = data
    a.run()