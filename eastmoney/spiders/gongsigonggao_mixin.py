# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import Request

class GongSiGongGaoMixin(object):
    def _gen_gongsigonggao_request(self,response):
        item = response.meta['item']
        url = "http://data.eastmoney.com/notice/%s.html"% item['_id']
        # 构造公司公告的链接
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