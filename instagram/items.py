# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TagItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    type = scrapy.Field()


class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    type = scrapy.Field()
