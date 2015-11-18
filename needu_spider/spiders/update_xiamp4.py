#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: xiamp4.py

from __future__ import print_function
import scrapy
import re
import needu_spider.db_films_save as dao
import phantomJS

'''
此爬虫只对xiamp4爬虫爬取到的数据进行更新，
该爬虫主要任务有：
    一：更新哪些电影属于热播电影
    二：更新全部电影数据详细信息，
           更新频率为每天更新一次，更新数据源（从数据库中抽取符合更新条件的数据）
           注意：由于此站点电影评分属性尤为特殊，用ajax动态加载的，由于无法分析其算法
                      所以决定在此爬虫初始化时，起一个新的进程调用phantomJS引擎对详细数据页面
                      进行渲染后再进行分析抓取

Author: xianyu.ying
Date: 2015-11-17
'''

class update_xiamp4(scrapy.spiders.Spider):

    name = 'update_xiamp4'

    #入口请求页面地址
    start_urls = [
        'http://www.xiamp4.com/'
    ]

    def __init__(self):
        self.logger.info('update_xiamp4 spider is starting now ...')
        self.debug = False   #debug 开关

        #这里先将本站原有的热播电影置空
        dao.resetHot('http://www.xiamp4.com/')

        #启动新进程(在phantomJS.py中启动)调用phantomJS接口模块
        phantomJS.call()


    #TODO(xianyu.ying): 爬虫的默认回调函数
    def parse(self, response):
        '''
        此爬虫只会调用一次该函数，因为只请求一个页面来分析每周热播
        所以进行直接处理，不传输给pipeline管道
        '''

        #单条数据调试用
        if self.debug:
            self.logger.info('debug is starting now ...')
            yield self.__process_data(response)  #清洗出数据看看长什么样子

        #根据已分析的首页页面结构提取节点数据
        #如果提取失败就丢弃
        sel = scrapy.selector.Selector(response)
        index = sel.xpath(r'//*[@id="main"]/div/div/div[@class="bd clearfix"]').extract()
        if index:
            #将获取到的节点数据，清洗出干净的数据
            cleanData = []
            tmp = re.findall(r'<a class="play-img".*?title=', index[0])
            for i in tmp:
                try:
                    s = i[i.index('/Html') : i.index('.html') + 5]
                    cleanData.append({'webFrom' : 'http://www.xiamp4.com/', 'filmId' : 'http://www.xiamp4.com' + s})
                except:
                    self.logger.error('This data can\'t to clean: ' + i)

            #调用数据库模块更新
            self.logger.info('Call db to update...')
            dao.updateHot(cleanData)