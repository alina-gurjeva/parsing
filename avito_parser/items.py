# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AvitoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field() 
    # Ссылка на объявление
    link = scrapy.Field()
    # Наименование объявления
    name = scrapy.Field()
    # Автор
    author = scrapy.Field()
    # Цена
    price = scrapy.Field()
    # Адресс
    address = scrapy.Field()
    # Параметры
    parameters = scrapy.Field()
    # Фото
    photos = scrapy.Field()
    pass
