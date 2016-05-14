# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import Request

class GuYouHuiMixin(object):
    def __init__(self):
        self.num = {}
        self.time = {}
        self.flag = {}

    def _gen_guyouhui_request(self,response):
        item = response.meta['item']
        item['numbergu'] = {}
        url = 'http://guba.eastmoney.com/list,%s,5,f_1.html' % item['_id']

        self.num[item['_id']] = 0
        self.time[item['_id']] = []
        self.flag[item['_id']] = False

        # 构造股友会按发帖时间排序的链接
        return Request(url, meta={'item':item}, callback=self.parse_guyouhui)

    def parse_guyouhui(self,response):
        item = response.meta['item']
        i = 2
        while Selector(response).xpath('//div[@id="articlelistnew"]/div[%d]/span[5]'%i).extract():
            url = 'http://guba.eastmoney.com' + Selector(response).xpath('//div[@id="articlelistnew"]/div[%d]/span[3]/a/@href'%i).extract()[0] # 获取每条帖子对应的链接
            #print url
            a = len(Selector(response).xpath('//div[@id="articlelistnew"]/div/span[5]').extract()) # 获取当前页面的帖子的总条数
            item['numbergu'] = [
                int(Selector(response).xpath(u'//div[@class="pager"]/text()').extract()[0][28:-3]),
                (int(response.url[42:-5])-1)*80+a-1,
                int(response.url[42:-5])
            ] # 将【股友会总帖子条数，当前页面帖子条数，当前页面为第几页】三个数字传给下一个链接，方便后面判断是否跳转到下一页
            yield Request(url, meta={'item':item}, callback=self.parse_getguyouhui)
            i = i + 1

    def parse_getguyouhui(self,response):
        item = response.meta['item']

        if self.flag[item['_id']] == False:
            item['guyouhui'] = {}
        self.num[item['_id']] += 1

        dates = {}
        day = []
        time0 = Selector(response).xpath('//*[@id="zwconttb"]/div[2]/text()').extract()[0][4:14] # 爬取帖子的发帖时间
        k = 0
        for key in item:
            if key == 'guyouhui':
                break
            else:
                k = k + 1
        if k == len(item.keys()): # 判断item['guyouhui']是否存在
            item['guyouhui'] = {}
        k = 0
        for key in item['guyouhui']:
            if key == time0: # 判断该条帖子的发帖日期是否已经存在，如果存在，直接在对应的时间中添加该帖子的标题，作者，内容和评论。
                content = ""
                for data in Selector(response).xpath('//*[@id="zwconbody"]/div/text()').extract():
                    content = content + data
                item['guyouhui'][time0].append({
                    'date':time0,
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    #'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':content,
                    'comments':{} # 先初始化，后面再添加评论
                })
                break
            else:
                k = k + 1
        if k == len(item['guyouhui'].keys()): # 如果日期原先不存在
            if k == 30: # 判断是否已经爬满30天
                return item
            # 如果没有30天，在字典中添加一个键对
            item['guyouhui'][time0] = [{
                    'date':time0,
                    'title':Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0],
                    #'author':Selector(response).xpath('//*[@id="zwconttbn"]/strong/a/text()').extract()[0],
                    'content':Selector(response).xpath('//*[@id="zwconbody"]/div/text()').extract()[0],
                    'comments':{} # 先初始化，后面再添加评论
                }]
        day = item['guyouhui'][time0]
        for i in range(0, len(day)): # 遍历这篇帖子发帖日期对应的数组
            if day[i]['title'] == Selector(response).xpath('//*[@id="zwconttbt"]/text()').extract()[0]:
                j = 1 # 找到这篇帖子对应的字典
                while Selector(response).xpath('//*[@id="zwlist"]/div[%d]'%j).extract(): # 逐条爬取评论
                    time1 = Selector(response).xpath('//*[@id="zwlist"]/div[%d]/div[3]/div/div[2]/text()'%j).extract()[0][4:23] # 爬取评论时间
                    if Selector(response).xpath('//*[@id="zwlist"]/div[%d]/div[3]/div/div/span/a/text()'%j).extract(): # 爬取评论者的姓名
                        name = Selector(response).xpath('//*[@id="zwlist"]/div[%d]/div[3]/div/div/span/a/text()'%j).extract()[0]
                    else:
                        name = Selector(response).xpath('//*[@id="zwlist"]/div[%d]/div[3]/div/div/span/span/text()'%j).extract()[0]
                    comment = ''
                    for data in Selector(response).xpath('//*[@id="zwlist"]/div[%d]/div[3]/div/div[3]/child::text()'%j).extract(): # 爬取评论内容
                        comment = comment + data
                    day[i]['comments'][time1] = {
                        #'name':name,
                        'comment':comment
                    } # 将爬取到的内容存入字典
                    j = j + 1
                break
        item['guyouhui'][time0] = day
        '''
        num = 0
        for key in item['guyouhui']:
            num = num + len(item['guyouhui'][key])
        '''

        num = self.num[item['_id']]
        if time0 not in self.time[item['_id']]:
            self.time[item['_id']].append(time0)
        if len(self.time[item['_id']]) > 30:
            return item
        print '%s\t%d\t%d' % (item['_id'],num,len(self.time[item['_id']]))
        #print item['numbergu'][1]

        if item['numbergu'][1] < item['numbergu'][0] and num == item['numbergu'][1]: # 判断是否已经爬取完当前页面所有帖子的链接，能否跳转到下一页
            url = "http://guba.eastmoney.com/list,"+item['_id']+",5,f_"+str(item['numbergu'][2]+1)+".html"
            self.flag[item['_id']] = True
            return Request(url, meta={'item':item}, callback=self.parse_guyouhui)
        else:
            self.flag[item['_id']] = False
            return item