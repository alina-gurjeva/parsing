from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
# from avito_parser import settings
from avito_parser.spiders.avito import AvitoSpider

if __name__ == '__main__':
    crawling_settings = Settings()
    crawling_settings.setmodule("avito_parser.settings")
    
    Process = CrawlerProcess(settings = crawling_settings)
    Process.crawl(AvitoSpider)
    Process.start()