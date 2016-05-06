# -*- coding: utf-8 -*-

# Scrapy settings for eastmoney project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'eastmoney'

SPIDER_MODULES = ['eastmoney.spiders']
NEWSPIDER_MODULE = 'eastmoney.spiders'

DOWNLOADER_MIDDLEWARES = {
#    'cnblogs.middlewares.MyCustomDownloaderMiddleware': 543,
    #'eastmoney.middlewares.RandomUserAgent': 1, #随机user agent
    #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110, #此API已经弃用
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110, #代理需要用到
    #'eastmoney.middlewares.ProxyMiddleware': 100, #代理需要用到
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware':None,
    'eastmoney.rotate_useragent.RotateUserAgentMiddleware':400,
    'scrapy_crawlera.CrawleraMiddleware': 600, #crawlera代理用到
}

ITEM_PIPELINES = {
	'eastmoney.pipelines.MongoPipeline':300,
}

LOG_LEVEL = 'ERROR'
 
MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'eastmoney'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'eastmoney (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY=1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}
#COMMANDS_MODULE = 'eastmoney.commands'
# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'eastmoney.middlewares.RandomUserAgent': 1,
#     'eastmoney.middlewares.ProxyMiddleware': 100,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'eastmoney.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'eastmoney.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
#SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"