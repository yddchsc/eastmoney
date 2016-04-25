# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
import json

class HangyeyaowenSpider(CrawlSpider):
    name = "hangyeyaowen"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum"
    ]     #龙虎榜的数据请求链接
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

        # 如果想要爬取龙虎榜单上的股票信息，去掉上面的注释，将3改为想要爬取的股票的数量。并注释掉下面的6行代码。
        pages = [["http://quote.eastmoney.com/000002.html","000002",u"万科A"],["http://quote.eastmoney.com/600104.html","600104",u"上汽集团"],["http://quote.eastmoney.com/600519.html","600519",u"贵州茅台"]]
        for page in pages: 
            item = EastmoneyItem()
            item['_id'] = page[1] #得到股票的代码
            item['name'] = page[2]  #得到股票的名字    
            yield Request(page[0], meta={'item':item}, callback=self.parse_stock)
    def parse_stock(self,response):
        item = response.meta['item']
        if item['_id'] != "000002":
            url = "http://quote.eastmoney.com"+Selector(response).xpath('//body/@onload').extract()[0][17:-1] # 页面用js的onload函数跳转到主页面，截取这个链接。
        else: # 目前只发现万科A的股票的链接跟其它不一样，用上面的截取方法得到的链接是：http://quote.eastmoney.com000002.html
            url = "http://quote.eastmoney.com/SZ000002.html"
        return Request(url, meta={'item':item}, callback=self.parse_second)
    def parse_second(self,response):
        item = response.meta['item']
        url = Selector(response).xpath('//a[@id="cgyyt2"]/@href').extract()[0] # 爬取行业要闻的链接
        if url == "http://stock.eastmoney.com/hangye.html": #如果没有行业要闻，跳转到行业的主页面，则返回要闻数目为0
            item['hangyeyaowen'] = {"null":0}
            return item
        else:
            return Request(url, meta={'item':item}, callback=self.parse_hangyeyaowen)
    def parse_hangyeyaowen(self,response):
        item = response.meta['item']
        i = 1
        hangyeyaowen = 0
        if Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li[1]/span/text()').extract(): # 判断是否有行业要闻，是否为空页面
            for key in item:
                if key == 'hangyeyaowen': # 判断是否为爬取的第一页
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
        while Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']').extract(): # 逐条爬取行业要闻
            j = 1
            while Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li['+str(j)+']/span/text()').extract():
                time = Selector(response).xpath('//div[@class="list"]/ul['+str(i)+']/li['+str(j)+']/span/text()').extract()[0]
                if cmp(time[0:10],sStr1[0:10]) == 0: # 判断这条要闻的日期是否与上一条的相同
                    hangyeyaowen = hangyeyaowen + 1
                else:
                    day[str(sStr1[0:10])] = hangyeyaowen
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30: # 判断是否取满30天
                        item['hangyeyaowen'] = day
                        return item
                    hangyeyaowen = 1
                    sStr1 = time
                j = j + 1
            i = i + 1
        day[str(sStr1[0:10])] = hangyeyaowen
        item['hangyeyaowen'] = day
        if Selector(response).xpath(u'//a[@class="f12"]/@href').extract(): # 判断下一页的链接是否存在
            if Selector(response).xpath(u'//a[@class="f12"][2]/@href').extract(): # 判断是否有两个链接，如果有就选第二个
                url = u'http://stock.eastmoney.com/hangye/'+Selector(response).xpath(u'//a[@class="f12"][2]/@href').extract()[0]
            else: # 否则选第一个
                url = u'http://stock.eastmoney.com/hangye/'+Selector(response).xpath(u'//a[@class="f12"]/@href').extract()[0]
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_hangyeyaowen)