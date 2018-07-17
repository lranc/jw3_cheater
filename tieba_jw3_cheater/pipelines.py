# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
import numpy
from tieba_jw3_cheater.items import TiebaCheaterItem,TiebaUrlItem
class TiebaJw3CheaterPipeline(object):
	def __init__(self, mongo_uri, mongo_db,cheater_url_dict,noises_id_list):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
		self.cheater_url_dict = cheater_url_dict
		self.noises_id_list = noises_id_list

	@classmethod
	def from_crawler(cls,crawler):
		return cls(
			mongo_uri = crawler.settings.get('MONGO_URI'),
			mongo_db = crawler.settings.get('MONGO_DATABASE'),
			cheater_url_dict=crawler.settings.get('CHATER_RUL_DICT'),
			noises_id_list=crawler.settings.get('NOISES_ID_LIST')
			)

	def open_spider(self,spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]

	def close_spider(self,spider):
		self.client.close()
		with open('cheater_url_dict.json','w') as f:
			json.dump(self.cheater_url_dict,f)
		
		with open('noises_id_list.txt','w') as f:
			f.write(','.join(list(set(self.noises_id_list))))

	def process_item(self, item, spider):
		if isinstance(item,TiebaCheaterItem):
			self._process_cheater_db_item(item)
		else:
			if isinstance(item,TiebaUrlItem):
				self._process_update_url_dict_item(item)
			else:
				self._process_update_noises_item(item)
		return item

	def _process_cheater_db_item(self,item):
		self.db.tieba_jw3_cheater.insert(dict(item))

	def _process_update_url_dict_item(self,item):
		self.cheater_url_dict.update(item['cheater_url_dict'])

	def _process_update_noises_item(self,item):
		self.noises_id_list=numpy.append(self.noises_id_list,item['noises_id_list'])
