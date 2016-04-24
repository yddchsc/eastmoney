# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
import json

class GeguyanbaoSpider(CrawlSpider):
    name = "geguyanbao"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum"
    ]   #龙虎榜的数据请求链接
    def parse(self, response):
        # r = json.loads(Selector(response).xpath('//p/text()').extract()[0]) #在json数据页面提取字符串后转换为json格式
        # p = 0
        # while p < 3:
        #     url = "http://quote.eastmoney.com/"+r['Data'][0]['Data'][p].split('|')[0]+".html" #得到股票的主页面链接
        #     item = EastmoneyItem()
        #     item['_id'] = r['Data'][0]['Data'][p].split('|')[0] #得到股票的代码
        #     item['name'] = r['Data'][0]['Data'][p].split('|')[1]  #得到股票的名字    
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
        url = "http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=GGSR&js={\"data\":[(x)],\"pages\":\"(pc)\",\"update\":\"(ud)\",\"count\":\"(count)\"}&ps=25&p=1&code="+item['_id'] #得到股票个股研报数据请求的链接
        return Request(url, meta={'item':item}, callback=self.parse_geguyanbao)
    def parse_geguyanbao(self,response):
        item = response.meta['item']
        r = Selector(response).xpath('//body/p/text()').extract()[0] #对页面爬取json数据
        sStr1 = "null"
        geguyanbao = 0
        day = {}
        if r[0:23] != "{\"data\":[{stats:false}]":           
            sStr1 = json.loads(r)['data'][0]['datetime'][0:10] #判断json数据是否为空
            for key in item: # 判断键值geguyanbao是否存在
                if key == "geguyanbao": # 如果存在，判断页面的第一个日期是否在上一个页面存在
                    day = item['geguyanbao']
                    for a in day:
                        if cmp(a,sStr1) == 0: #如果存在，将上一个页面这个日期对应的数字赋值给geguyanbao变量，后面这个日期的数量在这个基础上增加。
                            geguyanbao = day[str(sStr1)] 
                            break                 
                    break
            loo = 0
            for a in day: #计算字典中研报的总数量
                loo = day[a] + loo
            loo = loo / 25 + 1 #计算当前页面为第几页
            if loo < int(json.loads(r)['pages']):   #判断当前页面是否为最后一页
                num = 25
            else: #如果为最后一页，计算页面研报的数量
                num = int(json.loads(r)['count']) - (loo-1) * 25
            lo = 0
            while lo < num:
                data = json.loads(r)['data'][lo]['datetime'][0:10]
                if cmp(data,sStr1) == 0: #判断该条研报的日期是否已经存在
                    geguyanbao = geguyanbao + 1 #如果存在，数量加1
                else: #如果不存在
                    day[str(sStr1)] = geguyanbao #将上一个日期的数量储存
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30: #判断是否取满30天，取满则返回item，结束爬取
                        item['geguyanbao'] = day
                        return item
                        break
                    geguyanbao = 1 #将日期数量归1
                    sStr1 = data #将这个新日期赋值给变量sStr1
                lo = lo + 1
            day[str(sStr1)] = geguyanbao
        day[str(sStr1)] = geguyanbao
        item['geguyanbao'] = day # 将结果赋值给item
        if loo < int(json.loads(r)['pages']): # 判断是否还有下一页，若有，则跳转
            url = "http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=GGSR&js={\"data\":[(x)],\"pages\":\"(pc)\",\"update\":\"(ud)\",\"count\":\"(count)\"}&ps=25&p="+str(loo+1)+"&code="+item['_id']
            return Request(url, meta={'item':item}, callback=self.parse_geguyanbao)
        else: #如果没有下一页，返回item
            return item