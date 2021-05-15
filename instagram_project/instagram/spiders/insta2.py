import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy

from instagram_project.instagram import credentials
from instagram_project.instagram.items import InstagramItem


class InstaSpiderOUT(scrapy.Spider):
    """
    about followings
    """
    name = 'insta2'
    allowed_domains = ['instagram_project.com']
    start_urls = ['https://instagram.com/']
    login = credentials.login
    password = credentials.password
    start_link = 'https://www.instagram.com/accounts/login/ajax/'
    users = credentials.users
    graphQLurl = 'https://www.instagram.com/graphql/query/?'
    hash_followIN = 'c76146de99bb02f6415203be841dd25a'
    hash_followOut = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response, *args, **kwargs):
        token = self.csrf_token(response.text)
        yield scrapy.FormRequest(self.start_link, method='POST',
                                 formdata={'username': self.login, 'enc_password': self.password},
                                 callback=self.parse_user,
                                 headers={'X-CSRFToken': token})

    def parse_user(self, response: HtmlResponse):
        answer = json.loads(response.text)
        if answer['authenticated']:
            for login in self.users:
                yield response.follow(f'/{login}', callback=self.followNext, cb_kwargs={'username': login})

    def csrf_token(self, text):
        token = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return token.split(':').pop().replace(r'"', '')

    def id_user(self, text, username):
        Uid = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(Uid).get('id', username)

    def followNext(self, response: HtmlResponse, username):
        userID = self.id_user(response.text, username)
        variables = {'id': userID, "include_reel": 'true',
                     "fetch_mutual": 'false', "first": 50}
        urlOut = f'{self.graphQLurl}query_hash={self.hash_followOut}&{urlencode(variables)}'

        yield response.follow(urlOut, callback=self.outafter,
                              cb_kwargs={'username': username,
                                         'userID': userID,
                                         'variables': deepcopy(variables)})

    def outafter(self, response: HtmlResponse, username, userID, variables):
        j_data = json.loads(response.text)
        data = j_data.get('data').get('user').get('edge_follow')
        isNext = data.get('page_info').get('has_next_page')
        if isNext:
            variables['after'] = data.get('page_info').get('end_cursor')

        urlOut = f'{self.graphQLurl}query_hash={self.hash_followOut}&{urlencode(variables)}'
        yield response.follow(urlOut, callback=self.outafter,
                              cb_kwargs={'username': username,
                                         'userID': userID,
                                         'variables': deepcopy(variables)})
        followings = data.get('edges')
        for f in followings:
            item = InstagramItem(
                user_id=userID,
                user=username,
                how='out',
                data=f,
                ava=f['node']['profile_pic_url'],
                name=f['node']['full_name'],
                login=f['node']['username']

            )
            yield item
            # then cycle until the other user is not founded:
            login_f = f['node']['username']
            if login_f in self.users:  # means that user was founded, stop program
                return
            else:
                yield response.follow(f'/{login_f}', callback=self.followNext, cb_kwargs={'username': login_f})
