# -*- coding: utf-8 -*-
import pymongo
 
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from pymongo import MongoClient

class GeguyaowenPipeline(object):
 
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
 
    def process_item(self, item, spider):
        if spider.name != 'geguyaowen':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        return item
class HangyeyaowenPipeline(object):
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "eastmoney"
    MONGODB_COLLECTION = "hangyeyaowen"
    def __init__(self):
        connection = pymongo.MongoClient(
            self.MONGODB_SERVER,
            self.MONGODB_PORT
        )
        db = connection[self.MONGODB_DB]
        self.collection = db[self.MONGODB_COLLECTION]
 
    def process_item(self, item, spider):
        if spider.name != 'hangyeyaowen':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        return item
class GongsigonggaoPipeline(object):
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "eastmoney"
    MONGODB_COLLECTION = "gongsigonggao"
    def __init__(self):
        connection = pymongo.MongoClient(
            self.MONGODB_SERVER,
            self.MONGODB_PORT
        )
        db = connection[self.MONGODB_DB]
        self.collection = db[self.MONGODB_COLLECTION]
 
    def process_item(self, item, spider):
        if spider.name != 'gongsigonggao':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        return item
class GeguyanbaoPipeline(object):
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "eastmoney"
    MONGODB_COLLECTION = "geguyanbao"
    def __init__(self):
        connection = pymongo.MongoClient(
            self.MONGODB_SERVER,
            self.MONGODB_PORT
        )
        db = connection[self.MONGODB_DB]
        self.collection = db[self.MONGODB_COLLECTION]
 
    def process_item(self, item, spider):
        if spider.name != 'geguyanbao':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        return item
class GuyouhuiPipeline(object):
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "eastmoney"
    MONGODB_COLLECTION = "guyouhui"
    def __init__(self):
        connection = pymongo.MongoClient(
            self.MONGODB_SERVER,
            self.MONGODB_PORT
        )
        db = connection[self.MONGODB_DB]
        self.collection = db[self.MONGODB_COLLECTION]
 
    def process_item(self, item, spider):
        if spider.name != 'guyouhui':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        # return item
class XinwenPipeline(object):
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "eastmoney"
    MONGODB_COLLECTION = "xinwen"
    def __init__(self):
        connection = pymongo.MongoClient(
            self.MONGODB_SERVER,
            self.MONGODB_PORT
        )
        db = connection[self.MONGODB_DB]
        self.collection = db[self.MONGODB_COLLECTION]

    def process_item(self, item, spider):
        if spider.name != 'xinwen':
            return item
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.save(dict(item))
        # return item