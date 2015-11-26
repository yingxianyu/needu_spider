#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: xiamp4.py

import urllib
import urllib2
import time

def test(vid, Referer):
	url = ('http://www.xiamp4.com/inc/ajax.asp?id=' + vid +
		'&action=videoscore&timestamp=' + str(int(time.time() * 1000)))

	user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'

	headers = {'User-Agent' : user_agent, 'X-Request-With' : 'XMLHttpRequest', 'Referer' : Referer}

	req = urllib2.Request(url, None, headers) 
	response = urllib2.urlopen(req)
	data = response.read()
	data = data.replace('[', '').replace(']', '')

	datas = data.split(',')  #d,t,s

	'var x=parseInt(d)+parseInt(t),y=(Math.round(s / x * 10) / 10.0) || 0; '

	x = float(datas[0]) + float(datas[1])
	y = round(float(datas[2]) / x * 10) / 10.0



	print(y)










if __name__ == '__main__':
	test('21584', 'http://www.xiamp4.com/Html/GP21584.html')
