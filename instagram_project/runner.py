from instagram.spiders.Insta import InstaSpiderIn
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pymongo import MongoClient
from instagram_project.instagram import credentials


def _search(search, second, chain, collection):
    while True:
        if second in search:
            break
        else:
            for s in search:
                chain.append(s)
                search = list(collection.find({'login': s}, {'user'}))
                if not search:
                    chain = []
                    continue  # something like that, but just now I don't know how make it to work
            if not chain:
                break
    return chain


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram_project.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstaSpiderIn
    )
    crawler_process.start()

    # to find a chain:
    session = MongoClient('localhost', 27017)
    base = session.get_database('insta')
    followers = base['followers']
    followings = base['followings']
    users = credentials.users
    first, second = users[0], users[1]
    chain = []
    search = list(followers.find({'login': first}, {'user'}))
    chain_res = _search(search, second, chain, followers)
    if not chain_res:
        search = list(followings.find({'login': first}, {'user'}))
        chain_res = _search(search, second, chain, followings)







