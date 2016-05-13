# -*- coding: utf-8 -*-
import pymongo
 
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from pymongo import MongoClient

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "eastmoney"

class MongoPipeline(object):
    def __init__(self,mongo_server, mongo_port,mongo_db_name):
        client = pymongo.MongoClient(mongo_server,mongo_port)
        db = client[mongo_db_name]
        self.collection = db['stock']

    def _valid(self,item):
        for data in item:
            if not data:
                return (False,data)
        return (True,None)
    
    def process_item(self, item, spider):
        valid,data = self._valid(item)
        if valid:
            #self.connection.save(dict(item))
            fil = {'_id':item['_id']}
            del item['_id']
            if 'xinwen' in item:
                xinwen = item['xinwen']
                self.collection.update_one(
                    filter=fil,
                    update={'$set':xinwen},
                    upsert=True
                )
            elif 'guyouhui' in item:
                guyouhui = item['guyouhui']
                self.collection.update_one(
                    filter=fil,
                    update={'$set':guyouhui},
                    upsert=True
                )
            else:
                self.collection.update_one(
                    filter=fil,
                    update={'$set':item},
                    upsert=True
                )
        else:
            raise DropItem("Missing {0}!".format(data))
        return item

    @classmethod
    def from_settings(cls,settings):
        ret = {
            'mongo_server':settings.get('MONGODB_SERVER',MONGODB_SERVER),
            'mongo_port':settings.get('MONGODB_PORT',MONGODB_PORT),
            'mongo_db_name':settings.get('MONGODB_DB',MONGODB_DB),
        }
        return cls(**ret)


