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

# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')

class GeguyanbaoSpider(BaseSpider):
    name = "geguyanbao"
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://data.eastmoney.com/stock/stockstatistic.html"
    ]    
    def parse(self, response):
        # get stock link
        i = 1
        while Selector(response).xpath('//*[@id="dt_1"]/tbody/tr['+str(i)+']/td[2]/a/@href').extract():
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
        url = Selector(response).xpath('//*[@class="titlea tunderlineno"]/@href').extract()[1]
        yield Request(url, meta={'item':item}, callback=self.parse_geguyanbao)
    def parse_geguyanbao(self,response):
        item = response.meta['item']
        day = {}
        g = ghost.Ghost()
        with g.start() as session:
            session.display = False
            session.wait_timeout = 999
            session.download_images = False
            page, extra_resources = session.open(response.url)
            page, extra_resources = session.wait_for_page_loaded()
            #result, extra_resources = session.click('#PageCont > a:nth-child(9)',0)
            response = response.replace(body=session.content)
            lo = 1
            loo = []
            while not loo:
                dates, extra_resources = session.evaluate("""
                (function () {
                    var i = 0;
                    for (i = 0; i < %s; i++){
                        var element = document.querySelector(%s);
                        var evt = document.createEvent("MouseEvents");
                        evt.initMouseEvent("click", true, true, window, 1, 1, 1, 1, 1,false, false, false, false, %s, element);
                        element.dispatchEvent(evt);
                    }
                    elems = document.getElementById('dt_1').getElementsByTagName('ul');
                    var dates = [];
                    for (i = 0; i < elems.length; i++) {
                        dates[i] = elems[i].getElementsByTagName('li')[0].innerText;
                    }
                    return dates;
                })();
                """ % (str(lo), repr('#PageCont > a:nth-child(9)'), str(0)))
                page, extra_resources = session.wait_for_page_loaded()
                response = response.replace(body=session.content)
                #session.sleep(1)
                if dates:
                    sStr1 = str(dates[0])
                else:
                    sStr1 = "null"
                geguyanbao = 0
                if day:
                    for a in day:
                        if cmp(a,sStr1) == 0:
                            geguyanbao = day[str(sStr1)]
                            break
                if dates:
                    for data in dates:
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
                day[str(sStr1)] = geguyanbao
                lo = lo + 1
                if Selector(response).xpath('//*[@id="PageCont"]/a[@class="nolink"]').extract():
                    loo = False
                else:
                    loo = True
            day[str(sStr1)] = geguyanbao
            item['geguyanbao'] = day
            return item