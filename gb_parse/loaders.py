import json


from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def get_description(script):
    description = json.loads(script)["description"]
    tags = [r'<p>', r'</p>', r'<br />', r'<strong>', r'</strong>',
            r'</li>', r'<li>', r'</ul>', r'<ul>']
    for tag in tags:
        description = description.replace(tag, "")
    return description


def get_author(author):
    author_keys = ["title", "website", "description"]
    for key in author_keys:
        try:
            author[key] = "".join(author[key])
        except:
            author[key] = None
    return author


class HHLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = Join("")
    salary_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    author_in = MapCompose(get_author)
    author_out = TakeFirst()
