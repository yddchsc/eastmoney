import redis

conn = redis.Redis()
conn.flushall()
conn.lpush('eastmoney:start_urls','http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum')
import os
os.system('scrapy crawl eastmoney_redis')