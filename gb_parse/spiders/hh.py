import scrapy
from ..loaders import HHLoader


class HHSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    _general_xpath = {
        "pages": '//a[@data-qa="pager-next"]/@href',
        "vacancy": '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        "author": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    _author_xpath = {
        "title": "//div[@class='company-header']//h1//text()",
        "web_url": "//a[@data-qa='sidebar-company-site']/@href",
        "description": "//div[@data-qa='company-description-text']//text()",
        "vacancies": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
    }

    _vacancy_xpath = {
        "title": "//h1//text()",
        "salary": "//p[@class='vacancy-salary']/span/text()",
        "description": "//script[@type='application/ld+json']/text()",
        "skills": "//span[@data-qa='bloko-tag__text']/text()",
    }

    def _get_follow(self, response, selector_str, callback):
        for url in response.xpath(selector_str):
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._general_xpath["pages"], self.parse
        )
        yield from self._get_follow(
            response, self._general_xpath["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = HHLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._vacancy_xpath.items():
            loader.add_xpath(key, xpath)
        try:
            author_id = response.xpath(self._general_xpath["author"]).get()
            link = f"https://hh.ru{author_id}"
            yield scrapy.Request(link, meta={'loader': loader}, callback=self.author_parse)
        except Exception as e:
            print(e)

    def author_parse(self, response):
        loader = response.meta["loader"]
        author = {"url": response.url}
        for key, xpath in self._author_xpath.items():
            author[key] = response.xpath(xpath).getall()
        loader.add_value("author", author)
        yield loader.load_item()
