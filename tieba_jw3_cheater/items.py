# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
class TiebaUrlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cheater_url_dict = scrapy.Field()  #{url_id:[latest_page,latest_floor,reply_count]}

class TiebaNoisesItem(scrapy.Item):
    noises_id_list = scrapy.Field()


class TiebaCheaterItem(scrapy.Item):

    cheater_url = scrapy.Field()  #贴子url
    url_id = scrapy.Field() #贴子id
    post_title = scrapy.Field()  #帖子标题
    floor_num = scrapy.Field()    #楼层数
    user_id = scrapy.Field()  #楼层id
    user_name=scrapy.Field()  #楼层姓名
    reply_content = scrapy.Field()  #举报内容
    image_url = scrapy.Field()   #举报内容图片
    floor_time = scrapy.Field()  #评论时间
    #reply_comment = scrapy.Field() #回复举报者的评论