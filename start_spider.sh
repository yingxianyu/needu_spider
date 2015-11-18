#!/bin/bash
# Filename: start_spider.sh
# This shell is to start some spider
# Author: xianyu.ying
# Date: 2015/11/16

logFile=/yxy/log/needu_spider/xiamp4_$(date +%Y%m%d%H%M%S).log
echo -e 'xiamp4 spider 正在提交后台执行...'
scrapy crawl xiamp4 --logfile=$logFile &
echo -e 'xiamp4 spider 提交完成，日志：' $logFile

logFile=/yxy/log/needu_spider/update_xiamp4_$(date +%Y%m%d%H%M%S).log
echo -e 'update_xiamp4 spider 正在提交后台执行...'
scrapy crawl update_xiamp4 --logfile=$logFile &
echo -e 'update_xiamp4 spider 提交完成，日志：' $logFile

exit 0
