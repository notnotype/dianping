"""
general_template
"""

import logging
from typing import List

from peewee import *

from spider import ResourceRoot
from spider import Spider

spider = Spider()
logger = logging.getLogger('spider')
res = ResourceRoot('resources')
db = SqliteDatabase('db.sqlite')


class Shop(Model):
    url = CharField()
    name = CharField()
    comment_count = IntegerField()
    common_price = FloatField()
    taste = FloatField()
    environment = FloatField()
    service = FloatField()
    # 位置
    position = CharField()
    tel = CharField()
    data = TextField()

    class Meta:
        database = db


class Comment(Model):
    username = CharField()
    # 星星
    star = IntegerField()
    # 正文
    text = CharField()
    date = DateTimeField()
    # 赞
    praise = IntegerField()
    # 来自哪个店铺
    shop = ForeignKeyField(Shop, backref='comment')

    class Meta:
        database = db


def parse_comment(resp: spider.Response) -> List[Comment]:
    """获取 'http://www.dianping.com/shop/l9ZszA41xUchPAwb' 的评论

    :param resp: http://www.dianping.com/shop/l9ZszA41xUchPAwb
    :return: List[Comment]
    """
    # 包装 comments
    return []


def parse_info(url: str):
    """直接解析 https://github.com/notnotype/dianping/invitations 包括评论

    :param url: like https://github.com/notnotype/dianping/invitations
    :return: None
    """
    # 包装post表
    # 请求url
    resp = spider.get(url)
    title = resp.css('title')
    title = resp.xpath('//title/test()')
    title = title[0].text

    # 包装 Shop
    shop = Shop()
    shop.url = url
    shop.tel = '45465-654564'
    # 包装评论
    comments = parse_comment(resp)
    for comment in comments:
        comment.save()

    # 在包装后
    shop.save()


def search(keyword: str, position: str):
    """生成器返回搜索页面的url每一页

    :param keyword:
    :param position:
    :return:
    """
    yield ''
    ...


def shop_page_generator(keyword: str, position: str) -> list:
    """生成店铺页面url

    :param keyword:
    :param position: 地点
    :return: url like http://www.dianping.com/shop/l9ZszA41xUchPAwb
    """
    for search_page in search(keyword, position):
        # 解析获得 'http://www.dianping.com/shop/l9ZszA41xUchPAwb'等url
        yield 'http://www.dianping.com/shop/l9ZszA41xUchPAwb'


def main():
    # 初始化数据库
    if not db.is_connection_usable():
        db.connect()
    if not db.table_exists(Shop):
        db.create_tables([Shop])
    if not db.table_exists(Comment):
        db.create_tables([Comment])

    keyword = input('input keyword: ')
    position = input('input position: ')

    for search_url in shop_page_generator(keyword, position):
        '''search_url = *
        [
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        ]
        '''
        # 解析保存数据
        parse_info(search_url)


if __name__ == '__main__':
    exit(main())
