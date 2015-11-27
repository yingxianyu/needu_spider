# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:

import scrapy

"""
此类抽象出电影应有的一些属性
Author: xianyu.ying

Date: 2015-11-17
"""
class Xiamp4(scrapy.Item):
    id = scrapy.Field() #数据库序列号
    flag = scrapy.Field() #标记，记录是否属于热播内容
    name = scrapy.Field() #名称
    year = scrapy.Field() #上映年份
    classification = scrapy.Field() #类型
    filmType1 = scrapy.Field() #电影类型，例：电影，电视剧，动画片
    filmType2 = scrapy.Field() #对filmType1进一步说明，例：恐怖片，欧美剧
    actor = scrapy.Field() #主演
    loc = scrapy.Field() #地区
    filmdesc = scrapy.Field() #剧情
    score = scrapy.Field() #评分
    director = scrapy.Field() #导演
    webfrom = scrapy.Field() #来源网站
    filmid = scrapy.Field() #来源网站影片编号
    filmremotepic = scrapy.Field() #影片图片
    filmlocpic = scrapy.Field() #影片本地图片
    download = scrapy.Field() #影片下载地址

    createtime = scrapy.Field() #创建时间
    updatetime = scrapy.Field() #更新时间

