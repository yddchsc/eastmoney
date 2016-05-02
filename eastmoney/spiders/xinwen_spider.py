# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from eastmoney.items import EastmoneyItem
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
import json

class XinwenSpider(CrawlSpider):
    name = "xinwen"
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
        url = 'http://guba.eastmoney.com/list,' + item['_id'] + ',1,f_1.html'  # 构造新闻按发帖时间排序的链接
        item['number'] = {}
        return Request(url, meta={'item':item}, callback=self.parse_xinwen)
    def parse_xinwen(self,response):
        item = response.meta['item']
        i = 2
        while Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[5]').extract():
            url = 'http://guba.eastmoney.com' + Selector(response).xpath('//div[@id="articlelistnew"]/div['+str(i)+']/span[3]/a/@href').extract()[0] # 获取每条新闻对应的链接
            a = len(Selector(response).xpath('//div[@id="articlelistnew"]/div/span[5]').extract()) # 获取当前页面的新闻的总条数
            item['number'] = [int(Selector(response).xpath(u'//div[@class="pager"]/text()').extract()[0][28:-3]),(int(response.url[42:-5])-1)*80+a-1,int(response.url[42:-5])]
            # 将【新闻总新闻条数，当前页面新闻条数，当前页面为第几页】三个数字传给下一个链接，方便后面判断是否跳转到下一页
            yield Request(url, meta={'item':item}, callback=self.parse_getxinwen)
            i = i + 1
    def parse_getxinwen(self,response):
        item = response.meta['item']
        dates = {}
        day = []
        time0 = Selector(response).xpath('//*[@id="zwconttb"]/div[2]/text()').extract()[0][4:14] # 爬取新闻的发表时间
        k = 0
        for key in item:
            if key == 'xinwen':
                break
            else:
                k = k + 1
        if k == len(item.keys()): # 判断item['xinwen']是否存在
            item['xinwen'] = {}
        k = 0
        for key in item['xinwen']:
            if key == time0: # 判断该条新闻的发表日期是否已经存在，如果存在，直接在对应的时间中添加该新闻的标题，作者，内容和评论。
                content = ''
                i = 0
                while i < len(Selector(response).xpath('//p/text()').extract()) - 3:
                    data = Selector(response).xpath('//p/text()').extract()[i]
                    content = content + data.encode("UTF-8",'ignore')
                    i = i + 1
                item['xinwen'][time0].append({
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    #'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':content,
                    'comments':{} # 先初始化，后面再添加评论
                })
            else:
                k = k + 1
        if k == len(item['xinwen'].keys()):# 如果日期原先不存在
            if k == 30: # 判断是否已经爬满30天
                return item
            # 爬取新闻内容
            content = ''
            i = 0
            while i < len(Selector(response).xpath('//p/text()').extract()) - 3:
                data = Selector(response).xpath('//p/text()').extract()[i]
                content = content + data.encode("UTF-8",'ignore')
                i = i + 1
            # 如果没有30天，在字典中添加一个键对
            item['xinwen'][time0] = [{
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    #'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':content,
                    'comments':{} # 先初始化，后面再添加评论
                }]
        # day = item['xinwen'][time0]
        # for i in range(0, len(day)): # 遍历这篇新闻发表日期对应的数组
        #     if day[i]['title'] == Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0]:# 找到这篇新闻对应的字典
        #         j = 1
        #         while Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']').extract():# 逐条爬取评论
        #             time1 = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[2]/text()').extract()[0][4:23] # 爬取评论时间
        #             if Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/a/text()').extract(): # 爬取评论者的姓名
        #                name = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/a/text()').extract()[0]
        #             else:
        #                 name = Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div/span/span/text()').extract()[0]
        #             comment = ''
        #             for data in Selector(response).xpath('//*[@id="zwlist"]/div['+str(j)+']/div[3]/div/div[3]/child::text()').extract(): # 爬取评论的内容
        #                 comment = comment + data
        #             day[i]['comments'][time1] = {
        #                 'name':name,
        #                 'comment':comment
        #             } # 将爬取到的内容存入字典
        #             j = j + 1
        #         break
        # item['xinwen'][time0] = day
        num = 0
        for key in item['xinwen']:
            num = num + len(item['xinwen'][key])
        if item['number'][1] < item['number'][0] and num == item['number'][1]: # 判断是否已经爬取完当前页面所有新闻的链接，能否跳转到下一页
            url = "http://guba.eastmoney.com/list,"+item['_id']+",1,f_"+str(item['number'][2]+1)+".html"
            return Request(url, meta={'item':item}, callback=self.parse_xinwen)
        else:
            return item