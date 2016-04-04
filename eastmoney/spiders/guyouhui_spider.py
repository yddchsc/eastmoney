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
import time

# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')

class GuyouhuiSpider(BaseSpider):
    name = "guyouhui"
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
        url = 'http://guba.eastmoney.com/list,' + item['_id'] + ',5,f.html'
        yield Request(url, meta={'item':item}, callback=self.parse_guyouhui)
    def parse_guyouhui(self,response):
        item = response.meta['item']
        i = 2
        while Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            url = 'http://guba.eastmoney.com' + Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@href').extract()[0]
            yield Request(url, meta={'item':item}, callback=self.parse_getguyouhui)
            time.sleep(1)
            i = i + 1
    def parse_getguyouhui(self,response):
        item = response.meta['item']
        dates = {}
        day = []
        time0 = Selector(response).xpath('//*[@id="zwconttb"]/div[2]/text()').extract()[0][4:14]
        k = 0
        for key in item:
            if key == 'guyouhui':
                break
            else:
                k = k + 1
        if k == len(item.keys()):
            item['guyouhui'] = {}
        k = 0
        for key in item['guyouhui']:
            if key == time0:
                for data in Selector(response).xpath('//*[@id="zwconbody"]/div/text()').extract():
                    content = content + data
                item['guyouhui'][time0].append({
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':content,
                    'comments':{}
                })
            else:
                k = k + 1
        if k == len(item['guyouhui'].keys()):
            item['guyouhui'][time0] = [{
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':Selector(response).xpath('//*[@id="zwconbody"]/div/text()').extract()[0],
                    'comments':{}
                }]
        day = item['guyouhui'][time0]
        for i in range(0, len(day)):
            if day[i]['title'] == Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0]:
                j = 1
                while Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']').extract():
                    time1 = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[2]/text()').extract()[0][4:23]
                    if Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/a/text()').extract():
                        name = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/a/text()').extract()[0]
                    else:
                        name = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/span/text()').extract()[0]
                    comment = ''
                    for data in Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[3]/child::text()').extract():
                        comment = comment + data
                    day[i]['comments'][time1] = {
                        'name':name,
                        'comment':comment
                    }
                    j = j + 1
                break
        item['guyouhui'][time0] = day
        yield item



