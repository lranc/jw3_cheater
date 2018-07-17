# -*-coding: utf-8 -*-
import scrapy
import re
import json
import requests
from scrapy.linkextractors import LinkExtractor 
from scrapy.spiders import CrawlSpider,Rule
from scrapy import Request
from tieba_jw3_cheater.items import TiebaCheaterItem,TiebaUrlItem,TiebaNoisesItem

from lxml import etree 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class Tieba_CheaterSpider(CrawlSpider):

	pattern0 = re.compile(r'\d{5}\d+|QQ|微信|VX|支付宝|欠|邮箱|@|扣扣|债|企鹅|骗|银行|账号',re.I) #判断是否可能是举报项
	pattern1 = re.compile(r'骗|欠')
	url_part = 'https://tieba.baidu.com/p/'
	url_part2 = 'https://tieba.baidu.com/'
	headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

	name = 'jw3_cheater'
	allowed_domains=['tieba.baidu.com']
	start_urls = ['https://tieba.baidu.com/f?kw=%E4%B9%BE%E5%9D%A4%E4%B8%80%E6%8E%B7&ie=utf-8']
	rules=(
		Rule(LinkExtractor(allow=r'f?kw=%E4%B9%BE%E5%9D%A4%E4%B8%80%E6%8E%B7&ie=utf-8&pn=50|100|150|200|250|300|350|400',restrict_xpaths=('.//div[@id="frs_list_pager"]')),#
			callback='parse_index_url',follow=True),
		)
	
	#rules=(
	#	Rule(LinkExtractor(allow=r'f?kw=%E4%B9%BE%E5%9D%A4%E4%B8%80%E6%8E%B7&ie=utf-8&pn=\d+',restrict_xpaths=('.//div[@id="frs_list_pager"]')),#
	#		callback='parse_index_url',follow=True),
	#	)
	
	with open('noises_id_list.txt','r') as f:
		noises_id_list = f.readlines()[0].split(',')
	new_noises=[]	#新噪点贴子id列表	

	try:
		with open('cheater_url_dict.json','r') as f:
			old_cheater_url_dict = json.load(f)
	except:
		old_cheater_url_dict = {}

	def parse_index_url(self,response):	#处理贴吧页面,爬取举报贴
		body = response.xpath('.//li[@class=" j_thread_list clearfix"]') #首页所有帖子主体	
			
		for i in body:
			data_dict = json.loads(i.xpath('@data-field').extract()[0])  #帖子的data数据
			#print(data_dict)
			url_id = str(data_dict['id'])   #帖子ID
			if url_id in self.noises_id_list:  
				#print(url_id+' was useless')
				pass				
			else:
				post_title = i.xpath('.//a[@class="j_th_tit "]/text()').extract_first()  #贴子标题
				post_body = i.xpath('.//div[contains(@class,"threadlist_abs")]/text()').extract_first().strip()  #贴子摘要
				if re.search(self.pattern0,post_body) or re.search(self.pattern0,post_title): #判断是否出现触发词
					print('进行第二次检索关键词',url_id)
					pri_judgement = self.pri_judge(url_id)  #出现触发词,调用prijudge,判断贴内是否出现骗|欠
					if pri_judgement: #出现严格触发词,与已爬取url.dict对比
						reply_count = i.xpath('.//span[@class="threadlist_rep_num center_text"]/text()').extract_first()
						if url_id in self.old_cheater_url_dict.keys(): #判断是否为新url_id
							if  int(reply_count)>int(self.old_cheater_url_dict[url_id][2]): #旧url_id 判断是否回复数增加
								page=self.old_cheater_url_dict[url_id][0]
								latest_floor=self.old_cheater_url_dict[url_id][1]
								cheater_url=self.url_part+url_id+'?pn='+ str(page)
								yield Request(url=cheater_url,
									meta={'cheater_url':cheater_url,
										'url_id':url_id,
										'post_title':post_title,
										'reply_count':reply_count,
										'latest_floor':latest_floor,
										'latest_page':page,
										#'old_cheater_url_dict':self.old_cheater_url_dict,
										'dont_merge_cookies':True},
									callback=self.parse_all_detail,
									)
							else:
								print(url_id+' 回复数未增加')
						else:	#url_id为新,parse_all_detail
							cheater_url = self.url_part+url_id
							try:
								latest_floor=old_cheater_url_dict[url_id]['1']
							except:
								latest_floor=0
							yield Request(url=cheater_url,
								meta={'cheater_url':cheater_url,
									'url_id':url_id,
									'post_title':post_title,
									'reply_count':reply_count,
									'latest_floor':latest_floor,
									'latest_page':1,
									#'old_cheater_url_dict':self.old_cheater_url_dict,
									'dont_merge_cookies':True},
								callback=self.parse_all_detail,
								)
					else:
						print(url_id+' 帖子首页无严格触发词')
						self.new_noises.append(url_id)
				else:
					self.new_noises.append(url_id)
		if len(self.new_noises)>0:
			NoisesItem=TiebaNoisesItem(noises_id_list=self.new_noises)					
			yield NoisesItem#将新噪点加入噪点文件

	def parse_all_detail(self,response):
		meta=response.meta
		reply_count=meta['reply_count']
		cheater_url = meta['cheater_url']
		url_id = meta['url_id']
		post_title = meta['post_title']
		latest_floor = meta['latest_floor']
		#cheater_url_dict =meta['old_cheater_url_dict']
		post_bodys = response.xpath('.//div[@id="j_p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "]')
		for i in post_bodys:
			data_dict = json.loads(i.xpath('@data-field').extract_first())
			floor_num = data_dict['content']['post_no']
			if int(floor_num)>int(latest_floor):
				meta['latest_floor'] = floor_num
				user_name = data_dict['author']['user_name']
				user_id = data_dict['author']['user_id']			
				post_id = str(data_dict['content']['post_id'])
				reply_content = data_dict['content']['content']
				#reply_content=i.xpath('.//div[@class="post_bubble_middle_inner"]/text()').extract()+i.xpath('.//div[@id="post_content_%s"]/text()'% post_id).extract()
				#image_url = i.xpath('.//div[@class="post_bubble_middle_inner"]/img/@src').extract()+i.xpath('.//div[@id="post_content_%s"]/img/@src'% post_id).extract()
				floor_time = i.xpath('.//div[@class="post-tail-wrap"]/span[class="tail-info"][-1]/text()').extract()[0]
				CheaterItem = TiebaCheaterItem(cheater_url=cheater_url,
												post_title=post_title,
												url_id=url_id,
												user_id=user_id,
												floor_num=floor_num,
												user_name=user_name,
												reply_content=reply_content,
												#image_url=image_url,
												floor_time=floor_time,
												)
				yield CheaterItem
			else:
				pass

		page_list_tool = response.xpath('.//li[@class="l_pager pager_theme_5 pb_list_pager"]/a/text()').extract()
		if re.search('下一页',','.join(page_list_tool)):
			print('进行翻页')
			next_url = response.xpath('.//li[@class="l_pager pager_theme_5 pb_list_pager"]/a[text()="下一页"]/@href').extract()[0]
			next_url=self.url_part2 + next_url
			page=(re.search(r'pn=(\d+)',next_url).group(1))
			meta['latest_page']=page
			meta['cheater_url']=next_url
			yield Request(next_url,
						callback = self.parse_all_detail,
						meta=meta)
		else:
			reply_count=meta['reply_count']
			latest_page = meta['latest_page']
			latest_floor= meta['latest_floor']
			new_cheater_url_dict={url_id:[latest_page,latest_floor,reply_count]}

			ChaterUrlItem = TiebaUrlItem(cheater_url_dict=new_cheater_url_dict)
			yield ChaterUrlItem

	def pri_judge(self,url_id): #初步判断是否贴子第一页是否有触发词
		url = self.url_part+url_id
		response = requests.get(url=url,headers=self.headers,verify=False)
		html = etree.HTML(response.content)
		print(url)
		post_bodys = html.xpath('.//div[@id="j_p_postlist"]')[0]
		s=etree.tostring(post_bodys).decode('unicode_escape',errors='ignore')
		return re.search(self.pattern1,s)

	#def write_noises_id_list(self,new_noises):  #更新noises_id_list
	#	with open('noises_id_list.txt','a') as f:
	#		f.write(','+','.join(new_noises))	

	#def update_cheater_url_dict(self,cheater_url_dict,new_cheater_dict):
		#return cheater_url_dict.update(new_cheater_dict)

		