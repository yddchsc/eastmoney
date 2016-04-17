# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
import json

class GongsigonggaoSpider(Spider):
    name = "gongsigonggao"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum"
    ]    
    def parse(self, response):
        r = json.loads(Selector(response).xpath('//p/text()').extract()[0])
        p = 0
        while p < 3:
            url = "http://quote.eastmoney.com/"+r['Data'][0]['Data'][p].split('|')[0]+".html"
            item = EastmoneyItem()
            item['_id'] = r['Data'][0]['Data'][p].split('|')[0]
            item['name'] = r['Data'][0]['Data'][p].split('|')[1]       
            yield Request(url, meta={'item':item}, callback=self.parse_stock)
            p = p + 1
    def parse_stock(self,response):
        item = response.meta['item']
        url = "http://data.eastmoney.com/notice/"+item['_id']+".html"
        return Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)
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
        if Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract() and Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract()[0] != "javascript:void(0);":
            url = u'http://data.eastmoney.com'+Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract()[0]
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)