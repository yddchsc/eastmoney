# -*- coding: utf-8 -*-

import scrapy
from scrapy_redis.spiders import RedisSpider
from geguyanbao_mixin import GeGuYanBaoMixin
from geguyaowen_mixin import GeGuYaoWenMixin
from gongsigonggao_mixin import GongSiGongGaoMixin
from guyouhui_mixin import GuYouHuiMixin
from hangyeyaowen_mixin import HangYeYaoWenMixin
from xinwen_mixin import XinWenMixin
import sys
from eastmoney import config
from eastmoney.items import EastmoneyItem

class EastMoneySpiderMixin(GeGuYanBaoMixin,
                            GeGuYaoWenMixin,
                            GongSiGongGaoMixin,
                            GuYouHuiMixin,
                            HangYeYaoWenMixin,
                            XinWenMixin
                        ):

    def parse_stock(self, response):
        if isinstance(self,GeGuYanBaoMixin):
            print 1
            yield self._gen_geguynbao_request(response)
        if isinstance(self,GeGuYaoWenMixin):
            print 2
            yield self._gen_geguyaowen_request(response)
        if isinstance(self,GongSiGongGaoMixin):
            print 3
            yield self._gen_gongsigonggao_request(response)
        if isinstance(self,GuYouHuiMixin):
            print 4
            yield self._gen_guyouhui_request(response)
        if isinstance(self,XinWenMixin):
            print 5
            yield self._gen_xinwen_request(response)
        if isinstance(self,HangYeYaoWenMixin):
            print 6
            yield self._gen_hangyeyaowen_request(response)

    def _gen_start_request(self):
        pages = config.TARGETS
        for page in pages: 
            item = EastmoneyItem()
            item['_id'] = page['_id'] #得到股票的代码
            item['name'] = page['name']  #得到股票的名字    
            yield scrapy.Request(page['url'], meta={'item':item}, callback=self.parse_stock)     

class EastMoneySpiderRedis(RedisSpider,EastMoneySpiderMixin):
    name = 'eastmoney_redis'
    redis_key = 'eastmoney:start_urls'
    def __init__(self, *args, **kwargs):
        #domain = kwargs.pop('domain', '')
        #self.alowed_domains = filter(None, domain.split(','))
        EastMoneySpiderMixin.__init__(self)
        RedisSpider.__init__(self,*args, **kwargs)

    def parse(self,response):
        for item in self._gen_start_request():
            yield item


