# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
import json

class GeguyaowenSpider(CrawlSpider):
    download_delay = 10 #防止被禁
    name = "geguyaowen"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum"
    ]    
    def parse(self, response):
        # r = json.loads(Selector(response).xpath('//p/text()').extract()[0])
        # p = 0
        # while p < 3:
        #     url = "http://quote.eastmoney.com/"+r['Data'][0]['Data'][p].split('|')[0]+".html"
        #     item = EastmoneyItem()
        #     item['_id'] = r['Data'][0]['Data'][p].split('|')[0]
        #     item['name'] = r['Data'][0]['Data'][p].split('|')[1]       
        #     yield Request(url, meta={'item':item}, callback=self.parse_stock)
        #     p = p + 1
        pages = [["http://quote.eastmoney.com/000002.html","000002",u"万科A"],["http://quote.eastmoney.com/600104.html","600104",u"上汽集团"],["http://quote.eastmoney.com/600519.html","600519",u"贵州茅台"]]
        for page in pages: 
            item = EastmoneyItem()
            item['_id'] = page[1] #得到股票的代码
            item['name'] = page[2]  #得到股票的名字    
            yield Request(page[0], meta={'item':item}, callback=self.parse_stock)
    def parse_stock(self,response):
        item = response.meta['item']    
        url = "http://so.eastmoney.com/Search.ashx?qw=("+item['_id']+")("+item['name']+")&qt=2&sf=0&st=1&cpn=1&pn=100&f=0&p=0" #构造搜索的数据请求链接
        return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
    def parse_geguyaowen(self,response):
        item = response.meta['item']
        a = Selector(response).xpath('//p/text()').extract()
        i = 0
        r = ""
        while i < len(a):
            r = r + a[i]
            i = i + 1
        r = r[15:-1] #截取json数据部分的字符串
        sStr1 = "null"
        geguyaowen = 0
        day = {}
        if r != "{\"State\":\"1\",\"KeyWord\":\"("+item['_id']+")("+item['name']+")\",\"SearchType\":2,\"SearchMode\":1,\"SortType\":\"1\",\"PageNo\":\"1\",\"Pages\":0,\"DataCount\":0,\"DataResult\":[]}": # 判断返回的数据结果是否为空
            sStr1 = json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][0:4]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][4:6]+"-"+json.loads(json.dumps(eval(r)))['DataResult'][0]['ShowTime'][6:8]
            for key in item:
                if key == "geguyaowen": # 判断键值geguyaowen是否存在
                    day = item['geguyaowen']
                    for a in day:   # 如果存在，判断页面的第一个日期是否在上一个页面存在
                        if cmp(a,sStr1) == 0: #如果存在，将上一个页面这个日期对应的数字赋值给geguyanbao变量，后面这个日期的数量在这个基础上增加。
                            geguyaowen = day[str(sStr1)]
                            break
                    break
            loo = int(json.loads(json.dumps(eval(r)))['PageNo']) # 获得当前页码
            if (int(json.loads(json.dumps(eval(r)))['Pages']) / 100) * 100 == int(json.loads(json.dumps(eval(r)))['Pages']):
                pages = int(json.loads(json.dumps(eval(r)))['Pages']) / 100
            else:
                pages = int(json.loads(json.dumps(eval(r)))['Pages']) / 100 + 1
            if loo < pages:
                num = 100
            else:
                num = int(json.loads(json.dumps(eval(r)))['Pages']) - (loo-1) * 100
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
            url = "http://so.eastmoney.com/Search.ashx?qw=("+item['_id']+")("+item['name']+")&qt=2&sf=0&st=1&cpn="+str(loo+1)+"&pn=100&f=0&p=0"
            return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
        else:
            return item