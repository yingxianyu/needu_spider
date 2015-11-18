#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: xiamp4.py

from __future__ import print_function
import scrapy
import needu_spider.items
import re
import needu_spider.db_films_save as dao

'''
此爬虫主要针对以下网站进行抓取数据：
    抓取网站影视库（该地址将抓取整个影视库）：http://www.xiamp4.com/search.asp
    爬虫会对爬到的数据和数据库里的数据进行简单的比对，如果该数据已经被记录，将会扔掉，因为会有更新项目对其进行更新，
    所以该爬虫的主要任务是找新数据，然后记录到数据库中等待更新爬虫对其进行更新
    至于每周热播，更新信息，用另外更新爬虫项目（update_xiamp4）进行更新

Author: xianyu.ying
Date: 2015-11-17
'''

class xiamp4(scrapy.spiders.Spider):

    name = 'xiamp4'

    #入口请求页面地址
    #根据已分析的网站规则，影视大全页面只有一个入口点，之后的分页，爬虫会根据抽取的分页页面特征进行分析爬取
    start_urls = [
        'http://www.xiamp4.com/search.asp'
        #'http://www.xiamp4.com/Html/GP22002.html'
    ]

    def __init__(self):
        self.debug = False
        self.currPage = 1  #当前页
        self.totalPage = 1  #总页数
        self.logger.info('xiamp4 spider is starting now ...')


    #TODO(xianyu.ying): 爬虫的默认回调函数，用于第一级抓取分析
    def parse(self, response):
        '''爬虫的默认回调函数，用于第一级抓取分析'''

        #单条数据调试用
        if self.debug:
            self.logger.info('debug is starting now ...')
            yield self.__process_data(response)  #清洗出数据看看长什么样子


        #根据已知的页面结构分析，如果页面有此结构，认为是我们需要爬到的页面内容
        #如果此页面不符合我们定义的页面特征则丢弃该页面，搜索下一个页面
        sel = scrapy.selector.Selector(response)
        search_page = sel.xpath(r'//*[@id="main"]/div[3]/div[@class="movielist"]').extract()
        if len(search_page) > 0:
            self.logger.info('process page: ' + str(self.currPage))

            #更新总页数
            pageData = sel.xpath(r'//*[@id="pages"]/span[1]/text()').extract()
            totalPage = re.search(r'/[1-9]*', pageData[0])
            if totalPage:
                self.totalPage = int(totalPage.group(0)[1:])
                self.logger.info('get total page is: ' + str(self.totalPage))

            #根据已分析出的页面结构抽取页面，然后清洗出详细页面的链接的地址
            #如果分析不到页面结构则跳过页面
            data = sel.xpath(r'//*[@id="main"]/div[3]/div[2]/ul/li/a').extract()
            if len(data) > 0:                
                hrefs = self.__getDetailHref(data)  #清洗出所有详细页面的链接地址，顺便清洗出评分

                #开始请求得到的详细页面链接地址列表，中间会把分数值传给处理层一起处理
                #根据获取到的连接地址，开始请求详细页面，
                #请求详细页面之前和数据库比对是否已经有被爬过的痕迹，有则丢弃
                #无则将爬取结果交给self.__getDetailPage进行数据清洗
                for i in hrefs:
                    if dao.isExists('http://www.xiamp4.com/', i['href']):
                        self.logger.info(i['href'] + ' is processed, skip it.')
                    else:
                        yield scrapy.Request(i['href'], meta={'score': i['score']}, callback=self.__getDetailPage)

        #如果当前页不是最后一页，那么一直递增爬取下去，直到最后一页
        if self.currPage < self.totalPage:
            self.currPage += 1
            yield scrapy.Request('http://www.xiamp4.com/search.asp?page=' + str(self.currPage))   #请求下一页内容


    #TODO(xianyu.ying): 分析数据连接，返回list集合
    def __getDetailHref(self, html):
        '''清洗出所有详细页面的链接地址，顺便清洗出该影片的评分'''

        hrefs = []
        for strs in html:
            match_href = re.search(r'href=".*?html"', strs)  #链接地址
            match_title = re.search(r'title=".*?"', strs)   #影片名称
            match_score = re.search(r'<i>.*?</i>', strs)  #评分

            score = '0' #评分
            if match_score:
                match_score = re.findall(r'[0-9|.]', match_score.group(0))
                score = ''
                for i in match_score:
                    score += i


            href = '' #连接
            if match_href and match_title:
                href = 'http://www.xiamp4.com' + match_href.group(0)[6:-1]

            hrefs.append({'href' : href, 'score' : score})

        return hrefs


    #TODO(xianyu.ying): 根据详细页面进行数据清洗,该函数作为爬虫请求后的回调函数
    def __getDetailPage(self, response):
        '''
        根据详细页面进行数据清洗
        如果抓取层级为第一层，建议先调用此函数，方便将来拓展
        如果请求层级为最后一层，建议之间调用__process_data(response)
        '''

        return self.__process_data(response)  #让pipelines 接管保存至数据库


    #TODO(xianyu.ying):  根据节点清洗出需要的详细数据，返回item
    def __process_data(self, response):
        '''将详细页面数据清洗，保存至item对象'''
        
        self.logger.info('process page: ' + response.url)

        item = needu_spider.items.Xiamp4()
        sel = scrapy.selector.Selector(response)
        data = sel.xpath(r'//*[@id="main"]/div[@class="view"]').extract()
        if data:

            #评分，该值为一级抓取时传送过来的
            score = '0'
            try:
                score = response.meta['score']
            except:
                flag = '0'

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

            #影片图片
            tmp = sel.xpath(r'//*[@id="main"]/div[2]/div[@class="pic"]/img/@src').extract()
            remotepic = tmp[0]

            #影片下载地址
            tmp = sel.xpath(r'//*[@class="ndownlist"]').extract()
            download = ''
            if tmp:
                tmpStr = re.search(r'GvodUrls.*?;', tmp[0])
                download = tmpStr.group(0)[tmpStr.group(0).index('"') + 1:-2]



            item['flag'] = '' #标记，记录是否属于热播内容，由于此爬虫为收集数据，所以不做细节判断,该值更新项目会对其进行更新
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

            return item
