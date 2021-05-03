import scrapy
from pymongo import MongoClient


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def _get_follow(self, response, selector_str, callback):
        for itm in response.css(selector_str):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )

    def car_parse(self, response):
        url = response.url
        title = response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first()
        pictures_items = response.css(".PhotoGallery_thumbnails__3-1Ob .PhotoGallery_thumbnailItem__UmhLO")
        pictures = [itm.attrib['style'][21:-1] for itm in pictures_items if 'background-image' in itm.attrib['style']]
        characteristics = []
        all_ch = response.css('.AdvertSpecs_row__ljPcX')
        for ch in all_ch:
            key = ch.css('.AdvertSpecs_label__2JHnS::text').extract_first()
            val = ch.css('.AdvertSpecs_data__xK2Qx::text').extract_first()
            if val is None:
                val = ch.css('.AdvertSpecs_data__xK2Qx .blackLink::text').extract_first()
            ch_dict = {key: val}
            characteristics.append(ch_dict)
        description = response.css('.AdvertCard_descriptionInner__KnuRi::text').extract_first()
        data = {
            "url": url,
            "title": title,
            'pictures': pictures,
            'characteristics': characteristics,
            'description': description
        }
        collection = MongoClient()["scrapy"]["autoyoula"]
        collection.insert_one(data)
