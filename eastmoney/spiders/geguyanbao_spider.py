# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
import json

class GeguyanbaoSpider(Spider):
    name = "geguyanbao"
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
        url = "http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=GGSR&js={\"data\":[(x)],\"pages\":\"(pc)\",\"update\":\"(ud)\",\"count\":\"(count)\"}&ps=25&p=1&code="+item['_id']
        return Request(url, meta={'item':item}, callback=self.parse_geguyanbao)
    def parse_geguyanbao(self,response):
        item = response.meta['item']
        r = Selector(response).xpath('//body/p/text()').extract()[0]
        sStr1 = "null"
        geguyanbao = 0
        day = {}
        if r[0:23] != "{\"data\":[{stats:false}]":           
            sStr1 = json.loads(r)['data'][0]['datetime'][0:10]
            geguyanbao = 0
            for key in item:
                if key == "geguyanbao":
                    for a in day:
                        if cmp(a,sStr1) == 0:
                            geguyanbao = day[str(sStr1)]
                            break
                    day = item['geguyanbao']
                    break
            loo = 0
            for a in day:
                loo = day[a] + loo
            loo = loo / 25 + 1
            if loo < int(json.loads(r)['pages']):
                num = 25
            else:
                num = int(json.loads(r)['count']) - (loo-1) * 25
            lo = 0
            while lo < num:
                data = json.loads(r)['data'][lo]['datetime'][0:10]
                if cmp(data,sStr1) == 0:
                    geguyanbao = geguyanbao + 1
                else:
                    day[str(sStr1)] = geguyanbao
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30:
                        item['geguyanbao'] = day
                        return item
                        break
                    geguyanbao = 1
                    sStr1 = data
                lo = lo + 1
            day[str(sStr1)] = geguyanbao
        day[str(sStr1)] = geguyanbao
        item['geguyanbao'] = day
        if loo < int(json.loads(r)['pages']):
            url = "http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=GGSR&js={\"data\":[(x)],\"pages\":\"(pc)\",\"update\":\"(ud)\",\"count\":\"(count)\"}&ps=25&p="+str(loo+1)+"&code="+item['_id']
            return Request(url, meta={'item':item}, callback=self.parse_geguyanbao)
        else:
            return item