# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spider import BaseSpider
import ghost
from PySide import QtWebKit

# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')
class HangyeyaowenSpider(BaseSpider):
    name = "hangyeyaowen"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://data.eastmoney.com/stock/stockstatistic.html"
    ]
    def parse(self, response):
        # get stock link
        i = 1
        while Selector(response).xpath('//*[@id="dt_1"]/tbody/tr['+str(i)+']/td[2]/a/@href').extract()[0]:
            url = Selector(response).xpath('//*[@id="dt_1"]/tbody/tr['+str(i)+']/td[2]/a/@href').extract()[0]
            i = i + 1
            yield Request(url, callback=self.parse_stock)
    def parse_stock(self,response):
        hxs=Selector(text=response.body)
        codes = hxs.xpath('//div[@class="qphox header-title mb7"]')
        item = EastmoneyItem()
        for code in codes:
            item['_id'] = code.xpath(
                '//*[@id="code"]/text()').extract()[0]
            item['name'] = code.xpath(
                '//h2/text()').extract()[0]
        url = Selector(response).xpath('//*[@id="tab3"]/li[2]/h3/a/@href').extract()[0]
        yield Request(url, meta={'item':item}, callback=self.parse_hangyeyaowen)
    def parse_hangyeyaowen(self,response):
        item = response.meta['item']
        i = 1
        hangyeyaowen = 0
        if Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li[1]/span/text()').extract():
            for key in item:
                if key == 'hangyeyaowen':
                    day = item['hangyeyaowen']
                    sStr1 = Selector(response).xpath('//div[@class="list"]/ul[1]/li[1]/span/text()').extract()[0]
                    for a in day:
                        if a == sStr1[0:10]:
                            hangyeyaowen = day[a]
                            break
                    break
                else:
                    sStr1 = Selector(response).xpath('//div[@class="list"]/ul[1]/li[1]/span/text()').extract()[0]
                    day = {}
        else:
            sStr1 = "null"
            for key in item:
                if key == 'hangyeyaowen':
                    day = item['hangyeyaowen']
                    break
                else:
                    day = {}
        while Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']').extract():
            j = 1
            while Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li['+str(j)+']/span/text()').extract():
                time = Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li['+str(j)+']/span/text()').extract()[0]
                if cmp(time[0:10],sStr1[0:10]) == 0:
                    hangyeyaowen = hangyeyaowen + 1
                else:
                    day[str(sStr1[0:10])] = hangyeyaowen
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30:
                        item['hangyeyaowen'] = day
                        return item
                    hangyeyaowen = 1
                    sStr1 = time
                j = j + 1
            i = i + 1
        day[str(sStr1[0:10])] = hangyeyaowen
        item['hangyeyaowen'] = day
        if Selector(response).xpath(u'//a[@class="f12"]/@href').extract():
            if Selector(response).xpath(u'//a[@class="f12"][2]/@href').extract():
                url = u'http://stock.eastmoney.com/hangye/'+Selector(response).xpath(u'//a[@class="f12"][2]/@href').extract()[0]
            else:
                url = u'http://stock.eastmoney.com/hangye/'+Selector(response).xpath(u'//a[@class="f12"]/@href').extract()[0]
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_hangyeyaowen)