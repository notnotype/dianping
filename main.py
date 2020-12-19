"""
general_template
"""

import logging

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


def get_comment(resp: spider.Response):
    # 包装 comment
    return []


def get_info(url: str):
    # 包装post表
    resp = spider.get(url)
    title = resp.css('title')
    title = resp.xpath('//title/test()')
    title = title[0].text

    # 包装
    shop = Shop()
    shop.url = url
    shop.tel = '45465-654564'
    # 包装评论
    comments = get_comment(resp)
    ...


def search(keyword, position):
    """生成器返回搜索页面的url"""
    ...


def main():
    ...


if __name__ == '__main__':
    exit(main())
