import redis
from time import sleep
from datetime import datetime
import getopt
import sys

REDIS_PORT = 6379

def log(text):
    print '[%s]:%s'%(datetime.now().strftime('%d/%m/%y %H:%M:%S'),text)

def ending(spider_name,conn):

    queue_key = '%s:requests'%spider_name
    while True:
        try:
            if conn.llen(queue_key) >0:
                log('start watching')
                break
            else:
                sleep(1)
        except Exception as e:
            print e
            sleep(1)

    while True:
        ret = conn.llen(queue_key)
        if ret ==0:
            log('ending')
            pipe = conn.pipeline()
            try:
                pipe.watch(queue_key)
                sleep(60)
                ret = pipe.llen(queue_key)
                if ret > 0:
                    pipe.unwatch()
                else:
                    break
            except redis.exceptions.WatchError:
                log('still working')
                pass
        else:
            log('working:%d'%ret)
            if ret <50:
                sleep(2)
            else:
                sleep(10)
            

    log('end')

argf = 'r:s:'
opts,args = getopt.getopt(sys.argv[1:],argf)
for o,a in opts:
    if o == '-s':
        spider_name = a
    if o == '-r':
        host_name = a
conn = redis.Redis(host_name,REDIS_PORT)
ending(spider_name,conn)