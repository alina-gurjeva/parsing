# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from instagram_project.instagram.items import InstagramItem


class InstagramPipeline:
    def __init__(self):
        session = MongoClient('localhost', 27017)
        self.bd = session.insta
    
    def process_item(self, item, spider):
        if item['how'] == 'out':
            name_col = 'followings'
        else:
            name_col = 'followers'

        collection = self.bd[name_col] 
        
        collection.insert_one(item)
        
        return item
