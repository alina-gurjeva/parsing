import scrapy
from scrapy.http import HtmlResponse
from avito_parser.items import AvitoItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru', 'img.avito.st']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']  # ищем комиксы
    button_next = "//span[contains(text(),'След')]"
    links = "//div[contains(@class,'iva-item-titleStep')]/a/@href"
    title = "//h1/span//text()"
    price = "//div[contains(@class,'item-price-wrapper')]//span[contains(@class,'js-item-price')]/@content"
    address = "//span[@class='item-address__string']//text()"
    author = "//div[@data-marker='seller-info/name']/a/@href"
    parametres = "//ul[@class='item-params-list']/li//text()"
    photos = "//div[@class='gallery-list-item-link']/img/@src"

    def parse(self, response, *args, **kwargs):
        nextb = response.xpath(self.button_next).extract_first()
        links = response.xpath(self.links).extract()

        for link in links:
            yield response.follow(link, callback=self.object_parse)

        if nextb:
            yield response.follow(nextb, callback=self.parse)

    def object_parse(self, response):
        # Ссылка на объявление
        link = response.url
        # Наименование объявления
        title = response.xpath(self.title).extract_first()
        # Цену
        price = response.xpath(self.price).extract_first()
        # Адрес
        address = response.xpath(self.address).extract_first()
        # Автор
        author = response.xpath(self.author).extract_first()
        # Параметры
        parameters = [x for x in response.xpath("//ul[@class='item-params-list']/li//text()").extract() if x != ' '
                     and x != '\n  ']
        photos = response.xpath(self.photos).extract()

        yield AvitoItem(link=link, name=title, author=author, price=price,
                        address=address, parameters=parameters, photos=photos)
