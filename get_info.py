#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-8-14 下午2:36
# @Author  : xiaofang
# @Site    : 
# @File    : get_info.py
# @Software: PyCharm Community Edition
"""
通过观察淘宝请求特征，对淘宝api链接进行访问以获得想要的数据
"""
import requests
import json
import time
from fake_useragent import UserAgent
import pymongo

con = pymongo.MongoClient()
taobao_db = con.python.taobao_db

ua = UserAgent()
header = {'User-Agent':ua.random}


class Taobao:
	"""
	这是一个解析淘宝api并获得想要数据的类
	"""

	def __init__(self, item):
		self.start_url = 'https://s.m.taobao.com/search?q='+item+'&search=%E6%8F%90%E4%BA%A4&tab=all&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=6&wlsort=6&style=list&closeModues=nav%2Cselecthot%2Conesearch&page=1'
		self.total_page = self.get_total_page()
		self.item = item

	def get_total_page(self):
		"""
		因为获得的数据中包含有总页数，所以用这个方法获取商品总页数
		:return:
		"""
		r = requests.get(self.start_url)
		info = json.loads(r.text)
		total_page = info['totalPage']
		return int(total_page)

	def get_all_info(self):
		"""
		获取所查找的所有商品信息
		:return:
		"""
		for i in range(1,self.total_page):
			url = 'https://s.m.taobao.com/search?q=' + self.item + '&search=%E6%8F%90%E4%BA%A4&tab=all&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=6&wlsort=6&style=list&closeModues=nav%2Cselecthot%2Conesearch&page='+ str(i)
			time.sleep(1)
			r = requests.get(url,headers=header)
			text = json.loads(r.text)
			for info in text['listItem']:
				item = {}
				item['name'] = info.get('name', [])
				item['area'] = info.get('area', [])
				item['isMobileEcard'] = info.get('isMobileEcard', [])
				item['originalPrice'] = info.get('originalPrice', [])
				item['price'] = info.get('price', [])
				item['priceWap'] = info.get('priceWap', [])
				item['priceWithRate'] = info.get('priceWithRate', [])
				item['url'] = info.get('url', [])
				item['pic_path'] = info.get('pic_path', [])
				yield item

	def write_to_mongo(self):
		"""
		如果有写如数据库的需要可以调用刺方法直接写入数据库
		"""
		count = 0
		for i in self.get_all_info():
			count += 1
			taobao_db.insert(i)
			print("已经成功写入{}条数据".format(count))

if __name__ == "__main__":
	taobao = Taobao('iphone7')
	taobao.write_to_mongo()