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

class GongsigonggaoSpider(BaseSpider):
    name = "gongsigonggao"
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
        url = Selector(response).xpath('//*[@class="fr w390 mb10"]/div/a/@href').extract()[0]
        yield Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)
    def parse_gongsigonggao(self,response):
        item = response.meta['item']
        i = 1
        gongsigonggao = 0
        if Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract():
            for key in item:
                if key == 'gongsigonggao':
                    day = item['gongsigonggao']
                    sStr1 = Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract()[0]
                    for a in day:
                        if a == sStr1:
                            gongsigonggao = day[sStr1]
                            break
                    break
                else:
                    sStr1 = Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract()[0]
                    day = {}
        else:
            sStr1 = "null"
            for key in item:
                if key == 'gongsigonggao':
                    day = item['gongsigonggao']
                    break
                else:
                    day = {}
        while Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']').extract():
            j = 1
            while Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']/li['+str(j)+']/span[@class="date"]/text()').extract():
                time = Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']/li['+str(j)+']/span[@class="date"]/text()').extract()[0]
                if cmp(time,sStr1) == 0:
                    gongsigonggao = gongsigonggao + 1
                else:
                    day[str(sStr1)] = gongsigonggao
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30:
                        item['gongsigonggao'] = day
                        return item
                    gongsigonggao = 1
                    sStr1 = time
                j = j + 1
            i = i + 1
        day[str(sStr1)] = gongsigonggao
        item['gongsigonggao'] = day
        if Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract():
            url = u'http://data.eastmoney.com'+Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract()[0]
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)