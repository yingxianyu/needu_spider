#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: db_films_save.py

__author__ = 'xianyu.ying'

'''
此模块对数据库表cux_films_wait_process操作进行封装
由于此模块只是封装数据库部分的操作，
所以各项函数执行时不会判断业务逻辑，直接进行写入数据库，
如果程序报错，只会捕捉数据库相关的异常

Author: xianyu.ying
Date: 2015-11-17
'''

import logging
import traceback
import db

logger = logging.getLogger('db_films_save')

# global  object:
engine = None
table = 'cux_films_wait_process'

#TODO(xianyu.ying): 创建数据库引擎
def __init__(func):
    def wrapper(*args, **kw):
        global engine

        if engine == None:
            engine = db.create_engine('needu', 'Needu.app', 'NEEDU_DB', '192.168.1.200', '8003')

        return func(*args, **kw)
    return wrapper

#TODO(xianyu.ying): 写入清洗后的item到数据库
@__init__
def save(item):
    logger.info('start save to db now: ' + item['filmid'])
    try:
        row = db.update('INSERT INTO ' + table + (r'''(
            hot, filmName, filmYear, filmType, actor, location,
            filmDesc, score, director, download, webFrom,
            webFromId, filmRemotePic, filmLocPic, createtime, updatetime)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,SYSDATE(),SYSDATE())'''),
            item['flag'], item['name'], item['year'], item['classification'], item['actor'],
            item['loc'], item['filmdesc'], item['score'], item['director'], item['download'],
            item['webfrom'], item['filmid'], item['filmremotepic'], item['filmlocpic'])

        if row > 0:
            logger.info('save to db success ' + item['filmid'])
        else:
            logger.error('save to db error ' + item['filmid'])

    except:
        logger.error(item['filmid'] + ',save to db error: ' + traceback.print_exc())

#TODO(xianyu.ying):根据ID值，更新数据库数据
@__init__
def update(item):
    logger.info('start update to db now: ' + item['filmid'])
    try:
        row = db.update('update ' + table + ' set ' + (r'''
            filmName = ?, filmYear = ?,
            filmType = ?, actor = ?, location = ?,
            filmDesc = ?, score = ?, director = ?,
            download = ?, filmRemotePic = ?,
            filmLocPic = ?, updatetime = SYSDATE()
            WHERE id = ?'''),
            item['name'], item['year'], item['classification'], item['actor'], item['loc'],
            item['filmdesc'], item['score'], item['director'], item['download'], item['filmremotepic'],
            item['filmlocpic'], item['id'])

        if row > 0:
            logger.info('update to db success ' + item['filmid'])
        else:
            logger.error('update to db error ' + item['filmid'])

    except:
        logger.error(item['filmid'] + ',update to db error: ' + traceback.print_exc())

#TODO(xianyu.ying): 根据webFrom, filmId更新电影为热播电影
@__init__
def updateHot(cleanData):
    if cleanData == None or len(cleanData) == 0:
        logger.error('No data to update film is hot!')
    else:
        for i in cleanData:
            try:
                row = db.update('update ' + table + r''' set hot='Y' ''' + (r'''where
                    webFrom = ? and webFromId = ?'''), i['webFrom'], i['filmId'])

                if row > 0:
                    logger.info('update to hot success! ' + i['filmId'])
                else:
                    logger.error('update to hot error!(May film hasn\'t been loaded into the database -_-) ' + i['filmId'])
            except:
                logger.error(i['filmId'] + ' : update to hot error: ' + traceback.print_exc())

#TODO(xianyu.ying): 根据webFrom重置每周热播标记
@__init__
def resetHot(webFrom):
    try:
        row = db.update('update ' + table + ''' set hot='' where webFrom=?''', webFrom)
        if row > 0:
            logger.info(webFrom + ' reset hot sucess!')
        else:
            logger.error(webFrom + ' reset hot error!')
    except:
        logger.error(webFrom + ' : reset hot error: ' + traceback.print_exc())

#TODO(xianyu.ying): 检查数据是否存在
@__init__
def isExists(webFrom, filmId):
    try:
        if webFrom == None or filmId == None:
            raise Exception('webFrom or filmId is None!')
        row = db.select(('select 1 from ' + table +
            ' where webFrom = ? and webFromId = ?'), webFrom, filmId)

        if len(row) > 0:
            return True

        return False
    except:
        logger.error(traceback.print_exc())


if __name__ =='__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(isExists(r'http://www.xiamp4.com/', r'http://www.xiamp4.com/Html/GP22067.html'))