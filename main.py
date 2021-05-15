import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram.spiders.instagram import InstagramSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstagramSpider
    )
    crawler_process.start()