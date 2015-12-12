#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: update_xiamp4_start.py

import os
import needu_spider.db as DB


if __name__ == '__main__':
    engine = DB.create_engine('needu', 'Needu.app', 'NEEDU_DB', '192.168.1.200', '8003')

    while True:
        datas = DB.select(''' SELECT count(*) ct FROM cux_films_wait_process WHERE DATE_FORMAT(updatetime, '%Y%m%d')< DATE_FORMAT(SYSDATE(), '%Y%m%d') ''')
        if datas[0].ct != 0:
            print('start update_xiamp4...')
            file = os.popen('./start_spider.sh update_xiamp4') #参数update_xiamp4-D 为后台执行，生成日志文件
            print(file.read())
        else:
            break
