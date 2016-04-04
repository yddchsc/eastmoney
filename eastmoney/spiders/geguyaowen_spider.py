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
import urllib

# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')

class GeguyaowenSpider(BaseSpider):
    name = "geguyaowen"
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
    def parse_stock(self,response):
        hxs=Selector(text=response.body)
        codes = hxs.xpath('//div[@class="qphox header-title mb7"]')
        item = EastmoneyItem()
        for code in codes:
            item['_id'] = code.xpath(
                '//*[@id="code"]/text()').extract()[0]
            item['name'] = code.xpath(
                '//h2/text()').extract()[0]
        url = Selector(response).xpath('//*[@id="tab3"]/li[1]/h3/a/@href').extract()[0]
        yield Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
    def parse_geguyaowen(self,response):
        item = response.meta['item']
        g = ghost.Ghost()
        with g.start() as session:
            #session.display = True
            session.user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0"
            session.wait_timeout = 999
            session.download_images = False
            page, extra_resources = session.open(response.url)
            page, extra_resources = session.wait_for_page_loaded()
            session.sleep(1)
            response = response.replace(body=session.content)
        i = 1
        geguyaowen = 0
        if Selector(response).xpath('//*[@id="rdiv"]/div['+str(i)+']/div[1]/div/span[1]/text()').extract():
            for key in item:
                if key == 'geguyaowen':
                    day = item['geguyaowen']
                    sStr1 = Selector(response).xpath('//*[@id="rdiv"]/div['+str(i)+']/div[1]/div/span[1]/text()').extract()[0]
                    for a in day:
                        if a == sStr1[0:10]:
                            geguyaowen = day[a]
                            break
                    break
                else:
                    sStr1 = Selector(response).xpath('//*[@id="rdiv"]/div['+str(i)+']/div[1]/div/span[1]/text()').extract()[0]
                    day = {}
        else:
            sStr1 = "null"
            for key in item:
                if key == 'geguyaowen':
                    day = item['geguyaowen']
                    break
                else:
                    day = {}
        while Selector(response).xpath('//*[@id="rdiv"]/div['+str(i)+']/div[1]/div/span[1]/text()').extract():
            time = Selector(response).xpath('//*[@id="rdiv"]/div['+str(i)+']/div[1]/div/span[1]/text()').extract()[0]
            if cmp(time[0:10],sStr1[0:10]) == 0:
                geguyaowen = geguyaowen + 1
            else:
                day[str(sStr1[0:10])] = geguyaowen
                k = 0
                for key in day:
                    k = k + 1
                if k >= 30:
                    item['geguyaowen'] = day
                    return item
                geguyaowen = 1
                sStr1 = time
            i = i + 1
        day[str(sStr1[0:10])] = geguyaowen
        item['geguyaowen'] = day
        if Selector(response).xpath(u'//*[@class="pagi"]/a[.="下一页"]/@href').extract():
            url = 'http://so.eastmoney.com/'+Selector(response).xpath(u'//*[@class="pagi"]/a[.="下一页"]/@href').extract()[0]
            url = urllib.unquote(urllib.unquote(url))
        else:
            return item
        return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)