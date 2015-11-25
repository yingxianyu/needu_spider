#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: xiamp4.py

from __future__ import print_function
import scrapy
import re
import needu_spider.db_films_save as dao
import needu_spider.items

'''
此爬虫只对xiamp4爬虫爬取到的数据进行更新，
该爬虫主要任务有：
    一：更新哪些电影属于热播电影
    二：更新全部电影数据详细信息，
           更新频率为每天更新一次，更新数据源（从数据库中抽取符合更新条件的数据）

Author: xianyu.ying
Date: 2015-11-17
'''

class update_xiamp4(scrapy.spiders.Spider):

    name = 'update_xiamp4'

    #入口请求页面地址
    start_urls = []

    def __init__(self):
        self.logger.info('update_xiamp4 spider is starting now ...')

        #这里先将本站原有的热播电影置空
        dao.resetHot('http://www.xiamp4.com/')

        #先弄10条数据需要更新的数据进去
        datas = dao.getTenDataToUpdate('http://www.xiamp4.com/')
        for i in datas:
            self.start_urls.append(i.webFromId)

        #把首页弄进去抓取每周热播
        self.start_urls.append('http://www.xiamp4.com/')


    #TODO(xianyu.ying): 爬虫的默认回调函数
    def parse(self, response):
        '''
        此回调函数会根据页面结构特征来区分是更新每周热播信息，
        还是更新详细电影数据信息
        每周热播内容一次即可全部取出，且更新字段简单，所以每周热播内容不传输
        给pipeline管道处理，直接调用数据库模块处理
        '''

        #根据已分析的首页页面结构提取节点数据
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

        #根据已分析的详细页面结构判断是否需要进行下一步处理
        else:
            detailPage = sel.xpath(r'//*[@id="main"]/div[@class="view"]')
            if detailPage:
                self.__processDetailPage(response)


    #TODO(xianyu.ying): 将详细页面的数据进行清洗，更新
    def __processDetailPage(self, response):
        '''
        由于数据库模块已经封装了更新详细电影数据的方法，
        所以这里清洗出的数据直接交由处理
        这样在下次拿出10条数据来更新时，可以避免拿出重复数据出来
        '''

        self.logger.info('process update page: ' + response.url)

        item = needu_spider.items.Xiamp4()
        sel = scrapy.selector.Selector(response)
        data = sel.xpath(r'//*[@id="main"]/div[@class="view"]').extract()
        if data:
            pass
