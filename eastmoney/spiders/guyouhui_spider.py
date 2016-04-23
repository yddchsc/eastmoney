# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spiders import BaseSpider
import json

class GuyouhuiSpider(Spider):
    name = "guyouhui"
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
        item['number'] = {}
        url = 'http://guba.eastmoney.com/list,' + item['_id'] + ',5,f_1.html'
        return Request(url, meta={'item':item}, callback=self.parse_guyouhui)
    def parse_guyouhui(self,response):
        item = response.meta['item']
        i = 2
        while Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            url = 'http://guba.eastmoney.com' + Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@href').extract()[0]
            a = len(Selector(response).xpath('//div[@id="articlelistnew"]/div/span[5]').extract())
            item['number'] = [int(Selector(response).xpath(u'//div[@class="pager"]/text()').extract()[0][28:-3]),(int(response.url[42:-5])-1)*80+a-1,int(response.url[42:-5])]
            yield Request(url, meta={'item':item}, callback=self.parse_getguyouhui)
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
                content = ""
                for data in Selector(response).xpath('//*[@id="zwconbody"]/div/text()').extract():
                    content = content + data
                item['guyouhui'][time0].append({
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':content,
                    'comments':{}
                })
                break
            else:
                k = k + 1
        if k == len(item['guyouhui'].keys()):
            if k == 30:
                return item
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
                        #'name':name,
                        'comment':comment
                    }
                    j = j + 1
                break
        item['guyouhui'][time0] = day
        num = 0
        for key in item['guyouhui']:
            num = num + len(item['guyouhui'][key])
        if item['number'][1] < item['number'][0] and num == item['number'][1]:
            url = "http://guba.eastmoney.com/list,"+item['_id']+",5,f_"+str(item['number'][2]+1)+".html"
            return Request(url, meta={'item':item}, callback=self.parse_guyouhui)
        else:
            return item