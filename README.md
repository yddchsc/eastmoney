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
+ redis
+ redis-python

#问题原因

+ 问题

	+ [twisted] CRITICAL: Unhandled error in Deferred:

+ scrapy版本太高

	+ 由[这里](https://github.com/scrapy/scrapyd/issues/110)得到的启发。
	+ 尝试安装scrapy0.24.6和scrapyd1.0.1后问题解决。
	+ 在问题解决之前，安装过Scrapy 0.14.4也没有出现这个问题，故猜测是scrapy版本过高的问题。

#运行方法

由于scrapy版本不同，运行所以spider的代码不能使用，目前还在重写。
apt-get update
apt-get install -y git
git clone https://github.com/yddchsc/eastmoney.git
cd eastmoney
sh build.sh

+ 起一终端, 运行 python ending.py -r $redis_server_host -s $spider_name
	- $redis_server_host指作为redis server的ip, 本地可用localhost
	- $spider_name指要监视的爬虫, 这里只eastmoney_redis一个
	- 故本地测试用` python ending.py -r localhost -s eastmoney_redis`命令即可
	python ending.py -r 120.25.96.184 -s eastmoney_redis



+ 另起一终端, 运行 python start_crawl.py -m $mode -s $spider_name --host $host_ip
	- $mode指运行模式, $mode为h则为host模式, 会立即启动爬虫, $mode为l则为leaf模式, 会等待任务队列有任务才启动爬虫
	- $spider_name同上
	- $host_ip指分布式模式中运行redis和mongodb的主机
	- 故本地测试用`python start_crawl.py -m h -s eastmoney_redis --host localhost`

	python start_crawl.py -m h -s eastmoney_redis --host 120.25.96.184

	python start_crawl.py -m l -s eastmoney_redis --host 120.25.96.184


+ ending.py运行结束后, 手动结束start_crawl.py, 因为后者不会主动结束
+ 先启动ending.py, 后启动start_crawl.py, ending的输出中, `start watching`和`ending`,`end`的时间戳间隔即为为爬虫运行时长

+ 程序运行完成用cd calculate命令进入calculate文件夹
+ 运行python main.py即可得到结果（如果爬取这三个三十天的数据，处理需要七分钟左右）