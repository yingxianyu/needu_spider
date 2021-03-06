#!/bin/bash
# Filename: start_spider.sh
# This shell is to start some spider
# Author: xianyu.ying
# Date: 2015/11/16




case $1 in
    "-D" )
            logFile=/yxy/log/needu_spider/xiamp4_$(date +%Y%m%d%H%M%S).log
            echo -e 'xiamp4 spider 正在提交后台执行...'
            scrapy crawl xiamp4 --logfile=$logFile &
            echo -e 'xiamp4 spider 提交完成，日志：' $logFile

            logFile=/yxy/log/needu_spider/update_xiamp4_$(date +%Y%m%d%H%M%S).log
            echo -e 'update_xiamp4 spider 正在提交后台执行...'
            scrapy crawl update_xiamp4 --logfile=$logFile &
            echo -e 'update_xiamp4 spider 提交完成，日志：' $logFile

            exit 0
        ;;
    "update_xiamp4")
            scrapy crawl update_xiamp4

            exit 0
        ;;
    "update_xiamp4-D")
            logFile=/yxy/log/needu_spider/update_xiamp4_$(date +%Y%m%d%H%M%S).log
            echo -e 'update_xiamp4 spider 正在提交后台执行...'
            scrapy crawl update_xiamp4 --logfile=$logFile &
            echo -e 'update_xiamp4 spider 提交完成，日志：' $logFile

            exit 0
        ;;
    "xiamp4")
            scrapy crawl xiamp4

            exit 0
        ;;
    "xiamp4-D")
            logFile=/yxy/log/needu_spider/xiamp4_$(date +%Y%m%d%H%M%S).log
            echo -e 'xiamp4 spider 正在提交后台执行...'
            scrapy crawl xiamp4 --logfile=$logFile &
            echo -e 'xiamp4 spider 提交完成，日志：' $logFile

            exit 0
        ;;
    "")
        echo -e 'You MUST input a parameter!'
        ;;
    *)
        echo -e 'Bad parameter!'
        ;;
esac



