# -*- coding: utf-8 -*-
import json
from urllib import urlencode
import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import Request

class GeGuYaoWenMixin(object):

    def _gen_geguyaowen_request(self,response):
        item = response.meta['item']
        domain = 'http://so.eastmoney.com'
        base_url = '/Search.ashx'
        qw = '(%s)(%s)'%(item['_id'],item['name'])
        qw = qw.encode('utf-8')
        url_args = {
            'qw':qw,
            'qt':2,
            'sf':0,
            'st':1,
            'cpn':1,
            'pn':100,
            'f':0,
            'p':0,
        }
        url = ''.join([domain,base_url,'?',urlencode(url_args)])
        print url
        return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)

    def parse_stock(self,response):
        return self._gen_geguyaowen_request(response)
    
    def parse_geguyaowen(self,response):
        item = response.meta['item']
        a = Selector(response).xpath('//p/text()').extract()
        i = 0
        r = ""
        while i < len(a):
            r = r + a[i]
            i = i + 1
        r = r[15:-1] #截取json数据部分的字符串
        try:
            jobj = json.loads(json.dumps(eval(r)))
        except Exception,e:
            print e
            return
        sStr1 = "null"
        geguyaowen = 0
        day = {}
        js_code = '{"State":"1","KeyWord":"(%s)(%s)","SearchType":2,"SearchMode":1,"SortType":"1","PageNo":"1","Pages":0,"DataCount":0,"DataResult":[]}'%(item['_id'],item['name'])
        if jobj and "DataResult" in jobj and jobj["DataResult"]:# 判断返回的数据结果是否为空

            show_time = jobj['DataResult'][0]['ShowTime']

            sStr1 = '-'.join([show_time[0:4],show_time[4:6],show_time[6:8]])
            for key in item:
                if key == "geguyaowen": # 判断键值geguyaowen是否存在
                    day = item['geguyaowen']
                    for a in day:   # 如果存在，判断页面的第一个日期是否在上一个页面存在
                        if cmp(a,sStr1) == 0: #如果存在，将上一个页面这个日期对应的数字赋值给geguyanbao变量，后面这个日期的数量在这个基础上增加。
                            geguyaowen = day[str(sStr1)]
                            break
                    break
            loo = int(jobj['PageNo']) # 获得当前页码
            if (int(jobj['Pages']) / 100) * 100 == int(jobj['Pages']):
                pages = int(jobj['Pages']) / 100 # 判断个股要闻总数是否为100的倍数来确定总页数
            else:
                pages = int(jobj['Pages']) / 100 + 1
            if loo < pages: # 确定当前页面要闻数量
                num = 100
            else:
                num = int(jobj['Pages']) - (loo-1) * 100
            lo = 0
            while lo < num:
                show_time = jobj['DataResult'][lo]['ShowTime']

                data = '-'.join([ show_time[0:4],show_time[4:6],show_time[6:8] ])# 从数据中截取该条要闻的日期
                if cmp(data,sStr1) == 0: # 判断日期是否相同，相同则数量加一
                    geguyaowen = geguyaowen + 1
                else: # 不同则将数量存入字典，并将新日期赋值给sStr1,数量归1。
                    day[str(sStr1)] = geguyaowen
                    k = 0
                    for key in day:
                        k = k + 1
                    if k >= 30: # 判断是否已经取满30天，取满则停止抓取数据，返回item
                        item['geguyaowen'] = day
                        return item
                        break
                    geguyaowen = 1
                    sStr1 = data
                lo = lo + 1
            day[str(sStr1)] = geguyaowen
        day[str(sStr1)] = geguyaowen
        item['geguyaowen'] = day
        
        if jobj and "DataResult" in jobj and jobj["DataResult"] and loo < pages: # 判断是否还有下一页，有则构造下一页的请求链接
            url = "http://so.eastmoney.com/Search.ashx?qw=(%s)(%s)&qt=2&sf=0&st=1&cpn=%d&pn=100&f=0&p=0"%(item['_id'],item['name'],loo+1 )
            return Request(url, meta={'item':item}, callback=self.parse_geguyaowen)
        else:
            print item
            return item