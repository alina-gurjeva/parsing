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


class InstagramPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        collection = f"{spider.name}_{item['type']}"
        self.db[collection].insert_one(ItemAdapter(item).asdict())
        return item


class ImagesInstagramPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            for x in item['data']["image_versions2"]["candidates"]:
                url = x['url']
                yield Request(url)
        except:
            pass

    def item_completed(self, results, item, info):
        value = item['data'].get("carousel_media", "image_versions2")
        if value == "carousel_media":
            item['data']["image_versions2"]["candidates"] = []
            for x in item['data'].get(value):
                x["image_versions2"]["candidates"] = [x[1] for x in results]
                item['data']["image_versions2"]["candidates"].append(x)
        else:
            item['data']["image_versions2"]["candidates"] = [itm[1] for itm in results]
        return item
