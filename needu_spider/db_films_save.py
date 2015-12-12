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
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,SYSDATE(),DATE_ADD(SYSDATE(), INTERVAL -1 DAY))'''),
            item['flag'], item['name'], item['year'], item['classification'], item['actor'],
            item['loc'], item['filmdesc'], item['score'], item['director'], item['download'],
            item['webfrom'], item['filmid'], item['filmremotepic'], item['filmlocpic'])

        if row > 0:
            logger.info('save to db success ' + item['filmid'])
        else:
            logger.error('save to db error ' + item['filmid'])

    except:
        logger.error(item['filmid'] + ',save to db error: ' + traceback.print_exc())

#TODO(xianyu.ying):根据webFrom, filmId值，更新数据库数据
@__init__
def update(item):
    logger.info('start update to db now: ' + item['filmid'])
    try:
        row = db.update('update ' + table + ' set ' + (r'''
            filmName = ?, filmYear = ?,
            filmType1 = ?, filmType2 = ?,
            filmType = ?, actor = ?, location = ?,
            filmDesc = ?, score = ?, scoreCount = ?, director = ?,
            download = ?, filmRemotePic = ?,
            filmLocPic = ?, updatetime = SYSDATE()
            WHERE webFrom = ? and webFromId = ? '''),
            item['name'], item['year'], item['filmType1'], item['filmType2'], item['classification'],
            item['actor'], item['loc'], item['filmdesc'], item['score'], item['scoreCount'],
            item['director'], item['download'],
            item['filmremotepic'], item['filmlocpic'], item['webfrom'], item['filmid'])

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
            logger.warning(webFrom + ' reset hot error or no hot film to reset!')
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

#TODO(xianyu.ying): 根据来源网站，获取100条需要更新的数据
@__init__
def getDataToUpdate(webFrom, page):
    """
    返回[{webFromId:xxxxx},{webfromId:xxxx}]
    """
    datas = []
    try:
        logger.info('get data range:' + str(page * 100) + ',' + str(page * 100 + 100))
        datas = db.select('select webFromId from ' + table +
                ''' where DATE_FORMAT(updatetime, '%Y%m%d') < DATE_FORMAT(SYSDATE(), '%Y%m%d')
                and webFrom = ? LIMIT ''' + str(page * 100)+ ''',100 ''', webFrom)
        return datas
    except:
        logger.error(traceback.print_exc())
        return datas


if __name__ =='__main__':
    logging.basicConfig(level=logging.DEBUG)

    datas = getTenDataToUpdate('http://www.xiamp4.com/')
    print(datas[0].webFromId)

