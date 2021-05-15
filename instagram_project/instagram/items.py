# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user = scrapy.Field()
    how = scrapy.Field()
    data = scrapy.Field()
    ava = scrapy.Field()
    name = scrapy.Field()
    login = scrapy.Field()
