# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
import json

class GeguyaowenSpider(CrawlSpider):
    name = "geguyaowen"
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
        url = "http://so.eastmoney.com/Search.ashx?qw=("+item['_id']+")("+item['name']+")&qt=2&sf=0&st=1&cpn=1&pn=10&f=0&p=0"
        return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
    def parse_geguyaowen(self,response):
        item = response.meta['item']
        a = Selector(response).xpath('//p/text()').extract()
        i = 0
        r = ""
        while i < len(a):
            r = r + a[i]
            i = i + 1
        r = r[15:-1]
        sStr1 = "null"
        geguyaowen = 0
        day = {}
        if r != "{\"State\":\"1\",\"KeyWord\":\"("+item['_id']+")("+item['name']+")\",\"SearchType\":2,\"SearchMode\":1,\"SortType\":\"1\",\"PageNo\":\"1\",\"Pages\":0,\"DataCount\":0,\"DataResult\":[]}":
            sStr1 = json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][0:4]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][4:6]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][6:8]
            for key in item:
                if key == "geguyaowen":
                    for a in day:
                        if cmp(a,sStr1) == 0:
                            geguyaowen = day[str(sStr1)]
                            break
                    day = item['geguyaowen']
                    break
            loo = int(json.loads(json.dumps(eval(r)))['PageNo'])
            if (int(json.loads(json.dumps(eval(r)))['Pages']) / 10) * 10 == int(json.loads(json.dumps(eval(r)))['Pages']):
                pages = int(json.loads(json.dumps(eval(r)))['Pages']) / 10
            else:
                pages = int(json.loads(json.dumps(eval(r)))['Pages']) / 10 + 1
            if loo < pages:
                num = 10
            else:
                num = int(json.loads(json.dumps(eval(r)))['Pages']) - (loo-1) * 10
            lo = 0
            while lo < num:
                data = json.loads(json.dumps(eval(r)))['DataResult'][lo]['ShowTime'][0:4]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][lo]['ShowTime'][4:6]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][lo]['ShowTime'][6:8]
                if cmp(data,sStr1) == 0:
                    geguyaowen = geguyaowen + 1
                else:
                    day[str(sStr1)] = geguyaowen
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30:
                        item['geguyaowen'] = day
                        return item
                        break
                    geguyaowen = 1
                    sStr1 = data
                lo = lo + 1
            day[str(sStr1)] = geguyaowen
        day[str(sStr1)] = geguyaowen
        item['geguyaowen'] = day
        if r != "{\"State\":\"1\",\"KeyWord\":\"("+item['_id']+")("+item['name']+")\",\"SearchType\":2,\"SearchMode\":1,\"SortType\":\"1\",\"PageNo\":\"1\",\"Pages\":0,\"DataCount\":0,\"DataResult\":[]}" and loo < pages:
            url = "http://so.eastmoney.com/Search.ashx?qw=("+item['_id']+")("+item['name']+")&qt=2&sf=0&st=1&cpn="+str(loo+1)+"&pn=10&f=0&p=0"
            return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
        else:
            return item