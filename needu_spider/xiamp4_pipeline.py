# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting

import db_films_save as dao
import logging
from scrapy.exceptions import DropItem
from scrapy.conf import settings

logger = logging.getLogger('xiamp4_pipeline')

"""
pipeline主要将清洗后的数据进行保存
这里是[抓取--清洗--分析--保存]中的最后两个流程

Author: xianyu.ying
Date: 2015-11-17
"""
class Pipeline(object):

    #TODO(xianyu.ying): 将spider传过来的数据进行保存
    def process_item(self, item, spider):

        #根据爬虫名称来进行数据传输至不同的地方，此模块只处理xiamp4 spider清洗后的item
        if spider.name == 'xiamp4':

            #获取当前日志模式是否为调试，如果为调试模式，将不对数据库进行操作
            log_level = settings['LOG_LEVEL']
            if log_level and log_level == 'DEBUG':
                self.__debug(item)
            else:
                dao.save(item)  #保存至数据库
                return item

    #TODO(xianyu.ying): 方便调试，将抓取信息输出
    def __debug(self, item):
        """程序调试用输出,程序会生成一个data文件在LOG_PATH配置的目录中"""

        logPath = settings['LOG_PATH']
        if logPath == None and logPath == '':
            logger.error('Please set the LOG_PATH in the settings.py file')
            return

        with open(logPath + item['name'] + '.data', 'w') as f:
            for (k, v) in dict(item).items():
                f.write(k + ':' + v + '\n\n')
