# eastmoney

a crawler by scrapy of eastmoney.com

# v1.0环境

+ Windows10
+ python2.7.8
+ scrapy1.0.5
+ pymongo
	+ [安装MongoDB](http://www.runoob.com/mongodb/mongodb-window-install.html)
	+ MongoChef：MongoDB的可视化工具，选择性安装
+ numpy
	+ 用来对爬取到的数据进行计算处理

# 运行方法

+ 打开cmd命令行
+ 进入eastmoney，scrapy.cfg的目录
+ 运行scrapy crawlall
+ 程序运行完成用cd calculate命令进入calculate文件夹
+ 运行python main.py即可得到结果

#环境

+ Windows7
+ python2.7.8
+ scrapy0.24.6
+ pip install scrapy-crawlera
+ pymongo
	+ [安装MongoDB](http://www.runoob.com/mongodb/mongodb-window-install.html)
	+ MongoChef：MongoDB的可视化工具，选择性安装
+ numpy
	+ 用来对爬取到的数据进行计算处理

#问题原因

+ 问题

	+ [twisted] CRITICAL: Unhandled error in Deferred:

+ scrapy版本太高

	+ 由[这里](https://github.com/scrapy/scrapyd/issues/110)得到的启发。
	+ 尝试安装scrapy0.24.6和scrapyd1.0.1后问题解决。
	+ 在问题解决之前，安装过Scrapy 0.14.4也没有出现这个问题，故猜测是scrapy版本过高的问题。

#运行方法

由于scrapy版本不同，运行所以spider的代码不能使用，目前还在重写。

+ 进入E:\MongoDB\bin，双击mongod.exe
+ 进入E:\MongoDB\mongochef，双击mongochef打开mongochef(可使用其它），选择Quick Connect,弹出对话框后点击connect即可
+ 打开cmd命令行
+ 进入eastmoney，scrapy.cfg的目录
+ 运行scrapy crawl geguyanbao 爬取个股研报
+ scrapy crawl geguyaowen 爬取个股要闻
+ scrapy crawl gongsigonggao 爬取公司公告
+ scrapy crawl guyouhui 爬取股友会
+ scrapy crawl hangyeyaowen 爬取行业要闻
+ scrapy crawl xinwen 爬取新闻
+ 程序运行完成用cd calculate命令进入calculate文件夹
+ 运行python main.py即可得到结果（如果爬取这三个三十天的数据，处理需要七分钟左右）