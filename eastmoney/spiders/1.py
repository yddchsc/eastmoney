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
            break
    def parse_stock(self,response):
        hxs=Selector(text=response.body)
        codes = hxs.xpath('//div[@class="qphox header-title mb7"]')
        item = EastmoneyItem()
        for code in codes:
            item['Id'] = code.xpath(
                '//*[@id="code"]/text()').extract()[0]
            item['name'] = code.xpath(
                '//h2/text()').extract()[0]
        url = 'http://guba.eastmoney.com/list,' + item['Id'] + ',5,f.html'
        yield Request(url, meta={'item':item}, callback=self.parse_guyouhui)
    def parse_guyouhui(self,response):
        item = response.meta['item']
        req = []
        dates = {}
        day = []
        i = 2
        T = False
        if Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            sStr1 = Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]/text()').extract()[0]        
        else:
            sStr1 = "null"
        while Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            sStr = Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]/text()').extract()[0]
            if cmp(sStr1,sStr) == 0:
                day.append({
                    'title':Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@title').extract()[0],
                    'author':Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[4]/a/text()').extract()[0],
                    'comment':{}
                    })
            else:
                if int(sStr1[0:2]) > 04:
                    T = True
                if T:
                    dates['2015-'+sStr1] = day
                else:
                    dates['2016-'+sStr1] = day
                k = 0
                for key in dates:
                    k = k + 1
                if k >= 30:
                    item['guyouhui'] = dates
                    break
                day = []
                day.append({
                    'title':Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@title').extract()[0],
                    'author':Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[4]/a/text()').extract()[0],
                    'comment':{}
                    })
                sStr1 = sStr
            i = i + 1
        if T:
            dates['2015-'+sStr1] = day
        else:
            dates['2016-'+sStr1] = day
        item['guyouhui'] = dates
        i = 2
        while Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            url = 'http://guba.eastmoney.com' + Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@href').extract()[0]
            print url
            r = Request(url, meta={'item':item}, callback=self.parse_getguyouhui)
            req.append(r)
            i = i + 1
        return req
    def parse_getguyouhui(self,response):
        item = response.meta['item']
        time = Selector(response).xpath('//*[@id="zwconttb"]/div[2]/text()').extract()[0][4:14]
        day = item['guyouhui'][time]
        for i in range(0, len(day)):
            if day[i]['title'] == Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0]:
                j = 1
                while Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']').extract():
                    time1 = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[2]/text()').extract()[0][4:]
                    day[i]['comment'][time1] = {
                        'name':Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/a/text()').extract()[0],
                        'comment':Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[3]/child::text()').extract()[0]
                    }
                    print day[i]['comment']
                    j = j + 1
                break
        item['guyouhui'][time] = day
        return item



