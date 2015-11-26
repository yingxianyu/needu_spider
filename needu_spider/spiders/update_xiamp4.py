#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: update_xiamp4.py

from __future__ import print_function
import scrapy
import re
import needu_spider.db_films_save as dao
import needu_spider.items
import time
import urllib
import urllib2

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

        #记录一下当前爬取了多少个数据
        self.count = 0


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
            #将获取到的节点数据，清洗出干净的数据(每周热播数据)
            cleanData = []
            tmp = re.findall(r'<a class="play-img".*?title=', index[0])
            for i in tmp:
                try:
                    s = i[i.index('/Html') : i.index('.html') + 5]
                    cleanData.append({'webFrom' : 'http://www.xiamp4.com/', 'filmId' : 'http://www.xiamp4.com' + s})
                except:
                    self.logger.error('This data can\'t to clean: ' + i)

            #调用数据库模块更新
            self.logger.info('Call db to update hot films ...')
            dao.updateHot(cleanData)

        #根据已分析的详细页面结构判断是否需要进行下一步处理
        else:
            #更新电影详细数据
            detailPage = sel.xpath(r'//*[@id="main"]/div[@class="view"]')
            if detailPage:
                self.__processDetailPage(response)

                #如果当前爬取的数量达到10个(我们一次性在数据库中取10条数据来更新)
                #那么就再取10条数据来更新，直到没有数据更新为止
                if self.count >= 10:
                    self.count = 0
                    self.logger.info('get ten datas to update ...')
                    datas = dao.getTenDataToUpdate('http://www.xiamp4.com/')
                    for i in datas:
                        yield scrapy.Request(i.webFromId)


    #TODO(xianyu.ying): 将详细页面的数据进行清洗，更新
    def __processDetailPage(self, response):
        '''
        由于数据库模块已经封装了更新详细电影数据的方法，
        所以这里清洗出的数据直接交由处理
        这样在下次拿出10条数据来更新时，可以避免拿出重复数据出来
        '''

        self.logger.info('process update page: ' + response.url)
        
        sel = scrapy.selector.Selector(response)
        data = sel.xpath(r'//*[@id="main"]/div[@class="view"]').extract()

        if data:
            item = needu_spider.items.Xiamp4()

            #名称
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[@class="wz"]/text()').extract()
            name = tmp[len(tmp) - 1].replace(u'»', '').strip()

            #上映年份
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[3]/ul/li[1]/text()').extract()
            year = tmp[0].strip()

            #类型
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[3]/ul/li[2]/a/text()').extract()
            classification = r'/'.join(tmp)

            #主演
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[3]/ul/li[3]/a/text()').extract()
            actor = r'/'.join(tmp)

            #地区
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[3]/ul/li[4]/text()').extract()
            loc = tmp[0].strip()

            #剧情
            tmp = sel.xpath(r'//*[@class="mox juqing"]/div[2]').extract()
            filmdesc = ''
            if tmp:
                filmdesc = tmp[0][21:-6]   #保留剧情html格式
            else:
                filmdesc = response

            #来源网站具体链接地址
            filmid = response.url

            #获取分数
            vid = response.url
            vid = vid[vid.index('/GP') + 3 : vid.index('.html')]
            score = self.__getScore(vid, response.url) #调用封装请求获取分数

            #影片图片
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[@class="pic"]/img/@src').extract()
            remotepic = tmp[0]

            #影片下载地址
            tmp = sel.xpath(r'//*[@class="ndownlist"]').extract()
            download = ''
            if tmp:
                tmpStr = re.search(r'GvodUrls.*?;', tmp[0])
                download = tmpStr.group(0)[tmpStr.group(0).index('"') + 1:-2]

            item['name'] = name #名称
            item['year'] = year #上映年份
            item['classification'] = classification #类型
            item['actor'] = actor #主演
            item['loc'] = loc #地区
            item['filmdesc'] = filmdesc #剧情
            item['score'] = score #评分
            item['director'] = '' #导演(该网站无导演)
            item['webfrom'] = 'http://www.xiamp4.com/' #来源网站
            item['filmid'] = filmid #来源网站具体链接地址，可用于id用
            item['filmremotepic'] = remotepic #影片图片
            item['filmlocpic'] = '' #影片本地图片,留空
            item['download'] = download #影片下载地址,获取影片迅雷下载地址，一个影片可能有多个地址，中间用"###"隔开

            #进行utf-8转码
            for (k, v) in dict(item).items():
                if isinstance(v, unicode):
                   item[k] = v.encode('utf-8')

            dao.update(item)
            self.count += 1


    #TODO(xianyu.ying): 封装一个获取分数的url请求，根据返回值计算分数
    def __getScore(self, vid, Referer):
        '''
        此处封装一个urllib2的请求，该请求会返回一个文本，类似[1183,0,8453]  [d,t,s]
        根据已经分析到的公式，我们可以计算用返回的文本计算出分数值

        请求地址：http://www.xiamp4.com/inc/ajax.asp?id=21946&action=videoscore&timestamp=1448546250369
        公式：var x=parseInt(d)+parseInt(t),y=(Math.round(s / x * 10) / 10.0) || 0; 
                    计算结果，y为分数，x为评论数
        '''
        url = ('http://www.xiamp4.com/inc/ajax.asp?id=' + vid +
                '&action=videoscore&timestamp=' + str(int(time.time() * 1000)))

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'

        headers = {'User-Agent' : user_agent, 'X-Request-With' : 'XMLHttpRequest', 'Referer' : Referer}

        req = urllib2.Request(url, None, headers) 
        response = urllib2.urlopen(req)
        data = response.read()
        data = data.replace('[', '').replace(']', '')

        datas = data.split(',')  #d,t,s

        try:
            x = float(datas[0]) + float(datas[1])
            y = round(float(datas[2]) / x * 10) / 10.0
        except:
            y = 0

        return y
