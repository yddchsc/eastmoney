# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    number = scrapy.Field()
    geguyaowen = scrapy.Field()
    hangyeyaowen = scrapy.Field()
    gongsigonggao = scrapy.Field()
    geguyanbao = scrapy.Field()
    guyouhui = scrapy.Field()
    xinwen = scrapy.Field()