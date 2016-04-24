# eastmoney

a crawler by scrapy of eastmoney.com

# 环境

+ Windows10
+ python2.7
+ scrapy
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
