#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: phantomJS.py

from __future__ import print_function
import needu_spider.db_films_save as dao
import needu_spider.db as db
import needu_spider.items
import re
import logging 
import multiprocessing

logger = logging.getLogger('phantomJS.py')

'''
此模块负责更新数据库中已经抓到的电影数据，主要流程：
	1) 调用数据库，抽取前一天的数据库出来，二个字段足矣(id, webFromID)
	2) 调用phantomJS引擎，对页面(webFromID)进行渲染
	3) 分析渲染后的页面，清洗数据
	4) 根据数据库id字段，把数据回传给数据库模块对其更新

外部只要调用此模块的call()函数即可完成调用

Author: xianyu.ying
Date: 2015-11-18
'''

#TODO(xianyu.ying): 外部只要调用此函数即可完成调用
def call():
	service = multiprocessing.Process(name='phantomJS  __process', target=__process)
	service.start()
	logger.info('phantomJS is called complete, please wait to process!')

def __process():
	name = multiprocessing.current_process().name
    	logger.info(name + '  is start')

    
    	logger.info(name + '  is end successful!')