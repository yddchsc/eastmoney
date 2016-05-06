import redis
import sys
import getopt
import os
from time import sleep

REDIS_PORT = 6379
argf = 'm:s:'
argl = ['host=']
opts,args = getopt.getopt(sys.argv[1:],argf,argl)
for o,a in opts:
    if o == '-m':
        mode = a
    if o == '-s':
        spider_name = a
    if o == '--host':
        host_name = a

mongo_server = host_name
mongo_setting = 'MONGODB_SERVER=%s'%mongo_server
redis_setting = 'REDIS_HOST=%s'%host_name
cmd = 'scrapy crawl %s -s %s'%(spider_name,' -s '.join([mongo_setting,redis_setting]))

if mode == 'h':#host mode
    conn = redis.Redis(host_name,REDIS_PORT)
    conn.flushall()
    conn.lpush('eastmoney:start_urls','http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/LHBXQSUM/GetLHBXQSUM?tkn=eastmoney&mkt=0&dateNum=&startDateTime=2016-01-15&endDateTime=2016-04-15&sortRule=1&sortColumn=&pageNum=1&pageSize=50&cfg=lhbxqsum')
    os.system(cmd)

else:#leaf mode
    conn = redis.Redis(host_name,REDIS_PORT)
    queue_key = '%s:requests'%spider_name
    while True:
        try:
            if conn.llen(queue_key) >0:
                break
            else:
                sleep(1)
        except Exception as e:
            print e
            sleep(1)
    os.system(cmd)

