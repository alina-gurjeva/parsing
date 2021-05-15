import json
import datetime
import scrapy
from ..items import TagItem, PostItem
from ..loaders import TagLoader, PostLoader
from .. import credentials


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com", "i.instagram.com"]
    start_urls = ["https://www.instagram.com/accounts/login/"]
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    pagin_post_url = 'https://i.instagram.com/api/v1/tags/'
    x_ig_app_id = '936619743392459'
    tags = credentials.tags
    login = credentials.login
    password = credentials.password
    path = "/explore/tags/"

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                for tag in self.tags:
                    yield response.follow(f"{self.path}{tag}/", callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        answer_js = self.js_data_extract(response)
        item = TagItem()
        tag_loader = TagLoader(item=item)
        yield from self.top_parse(answer_js)
        yield from self.recent_parse(answer_js)
        tag_loader.add_value("date_parse", datetime.datetime.now())
        tag_loader.add_value("data", answer_js['entry_data']['TagPage'][0]['data'])
        tag_loader.add_value("type", 'tags')
        yield tag_loader.load_item()

    def top_parse(self, answer_js):
        pag = answer_js['entry_data']['TagPage'][0]['data'].pop('top')
        sections = pag.pop('sections')
        for section in sections:
            for media in section['layout_content']['medias']:
                result = {}
                result.update(media['media'])
                result.update(pag)
                item = PostItem()
                post_loader = PostLoader(item=item)
                post_loader.add_value("date_parse", datetime.datetime.now())
                post_loader.add_value("data", result)
                post_loader.add_value("type", 'post')
                yield post_loader.load_item()

    def recent_parse(self, answer_js):
        pag = answer_js['entry_data']['TagPage'][0]['data'].pop('recent')
        tag_name = answer_js['entry_data']['TagPage'][0]['data']['name']
        token = answer_js["config"]["csrf_token"]
        if pag['more_available']:
            formdata = {"include_persistent": "0",
                        "max_id": pag['next_max_id'],
                        "page": str(pag['next_page']),
                        "surface": 'grid',
                        "tab": 'recent'}
            if pag['next_media_ids']:
                formdata['next_media_ids'] = [str(x) for x in pag['next_media_ids']]
            yield scrapy.FormRequest(
                f'{self.pagin_post_url}{tag_name}/sections/',
                method="POST",
                callback=self.pagination_follow,
                formdata=formdata,
                headers={"X-CSRFToken": token, "X-IG-App-ID": self.x_ig_app_id},
                meta={'token': token, 'tag_name': tag_name, 'type_post': 'recent'},
            )

    def pagination_follow(self, response):
        yield from self.type_post_parse(response)

    def type_post_parse(self, response):
        data = response.json()
        sections = data.pop('sections')
        for section in sections:
            for media in section['layout_content']['medias']:
                result = {}
                result.update(media['media'])
                result.update(data)
                item = PostItem()
                post_loader = PostLoader(item=item)
                post_loader.add_value("date_parse", datetime.datetime.now())
                post_loader.add_value("data", result)
                post_loader.add_value("type", 'post')
                yield post_loader.load_item()

    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData =')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
