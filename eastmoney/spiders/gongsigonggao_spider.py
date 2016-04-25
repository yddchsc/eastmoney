# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
import json

class GongsigonggaoSpider(CrawlSpider):
    name = "gongsigonggao"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum"
    ]    #龙虎榜的数据请求链接
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
        url = "http://data.eastmoney.com/notice/"+item['_id']+".html" # 构造公司公告的链接
        return Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)
    def parse_gongsigonggao(self,response):
        item = response.meta['item']
        i = 1
        gongsigonggao = 0
        if Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract(): # 判断公司是否有公告
            for key in item:
                if key == 'gongsigonggao': # 判断这个页面是否为第一页
                    day = item['gongsigonggao']
                    sStr1 = Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract()[0]
                    for a in day:
                        if a == sStr1: # 判断当前页面第一个日期是否已经存储，如果已经存储，则将该日期对应的公告数赋值给变量gongsigonggao
                            gongsigonggao = day[sStr1]
                            break
                    break
                else: # 如果为第一页，将页面第一个日期赋值给sStr1
                    sStr1 = Selector(response).xpath('//div[@class="cont"]/ul[1]/li[1]/span[@class="date"]/text()').extract()[0]
                    day = {}
        else: # 如果当前页面没有公告
            sStr1 = "null"
            for key in item:
                if key == 'gongsigonggao':
                    day = item['gongsigonggao']
                    break
                else:
                    day = {}
        while Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']').extract(): # 逐条爬取公告日期
            j = 1
            while Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']/li['+str(j)+']/span[@class="date"]/text()').extract():
                time = Selector(response).xpath('//div[@class="cont"]/ul['+str(i)+']/li['+str(j)+']/span[@class="date"]/text()').extract()[0]
                if cmp(time,sStr1) == 0: # 如果新爬取的日期与前面的日期相同，日期对应的数量加1
                    gongsigonggao = gongsigonggao + 1
                else: # 否则，将日期与日期对应的数量用字典存储起来
                    day[str(sStr1)] = gongsigonggao
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30: # 判断是否取满30天的公告
                        item['gongsigonggao'] = day
                        return item
                    gongsigonggao = 1
                    sStr1 = time
                j = j + 1
            i = i + 1
        day[str(sStr1)] = gongsigonggao
        item['gongsigonggao'] = day
        if Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract() and Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract()[0] != "javascript:void(0);": # 判断页面是否还有下一页
            url = u'http://data.eastmoney.com'+Selector(response).xpath(u'//*[@id="PageCont"]/a[.="下一页"]/@href').extract()[0]
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_gongsigonggao)