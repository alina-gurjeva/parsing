# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from .settings import BOT_NAME
from pymongo import MongoClient


class AvitoPipeline:
    def process_item(self, item, spider):
        return item


class AvitoMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        parameters = item['parameters']
        keys = [parameters[i] for i in range(len(parameters)) if i % 2 == 0]
        values = [parameters[i] for i in range(len(parameters)) if i % 2 != 0]
        item['parameters'] = {k:v for k,v in zip(keys, values)}
        self.db[spider.name].insert_one(item)
        return item


class AvitoImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get("photos", []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if item.get("photos"):
            item["photos"] = [itm[1] for itm in results]
        return item
