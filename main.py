"""
general_template
"""

import logging
from itertools import count
from typing import List
from urllib.parse import quote

from peewee import *
from fake_useragent import UserAgent
from lxml.html import HtmlElement

from spider import ResourceRoot
from spider import Spider

spider = Spider()
logger = logging.getLogger('spider')
res = ResourceRoot('resources')
db = SqliteDatabase('db.sqlite')


def header_generator():
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'max-age=0',
        'Host': 'www.dianping.com',
        'Referer': 'http://www.dianping.com/beijing/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': str(UserAgent().random),
    }
    return header


def response_pipeline(s: Spider, response: Spider.Response):
    while response.title == '验证中心':
        input('去验证: {}'.format(response.url))
        response = spider.get(response.history[0], cache=Spider.DISABLE_CACHE)
    return response


# 设置爬虫
spider.headers_generator = header_generator
# 让它去打开浏览器验证
spider.response_pipeline = response_pipeline
# 取消每次请求间隔时间
# spider.set_sleeper(lambda: None)


class Shop(Model):
    url = CharField()
    name = CharField(unique=True)
    items_info = []
    comment_count = IntegerField()
    avg_price = FloatField()
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
    username = CharField(unique=True)
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
    """直接解析 http://www.dianping.com/shop/l9ZszA41xUchPAwb 包括评论

    :param url: like http://www.dianping.com/shop/l9ZszA41xUchPAwb
    :return: None
    """
    # 包装post表
    # 请求url

    # resp = spider.get(url, cache=Spider.DISABLE_CACHE)  关闭缓存
    resp = spider.get(url)
    shop_name = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/h1/text()|/html/body/div[2]/div/div[2]/div[1]/h1/e/text()')

    brief_info = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/div[1]')[0]
    star_num = brief_info.xpath('./span[1]/@class')
    comment_count = brief_info.xpath('./span[@id="reviewCount"]/text()|./span[@id="reviewCount"]/d/text()')
    avg_price = brief_info.xpath('./span[@id="avgPriceTitle"]/text()|./span[@id="avgPriceTitle"]/d/text()')

    comment_score = brief_info.xpath('./span[@id="comment_score"]')[0]
    taste = comment_score.xpath('./span[1]/text()|./span[1]/d/text()')
    environment = comment_score.xpath('./span[2]/text()|./span[2]/d/text()')
    service = comment_score.xpath('./span[3]/text()|./span[3]/d/text()')

    expand_info = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]')[0]
    position = expand_info.xpath('./div/span/text()|./div/span/e/text()').insert(0, "地址: ")

    tel = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/p')[0].xpath('./text()|./*/text()')

    print(shop_name, star_num, comment_count, avg_price, taste, environment, service, position, tel)

    '''暂时不包装到数据库'''
    # # 包装 Shop
    # shop = Shop()
    # shop.url = url
    # shop.name = shop_name
    # shop.items_info = brief_info
    # shop.position = position
    # shop.tel = tel
    # shop.comment_count = comment_count
    # shop.avg_price = avg_price
    # shop.taste = taste
    # shop.environment = environment
    # shop.service = service
    # shop.position = position
    # shop.data = 'data'
    # # 包装评论
    # comments = parse_comment(resp)
    # for comment in comments:
    #     comment.save()
    #
    # # 在包装后
    # shop.save()


def test_parse_info():
    parse_info('http://www.dianping.com/shop/l9ZszA41xUchPAwb')


def search(keyword: str, position: str):
    """生成器返回搜索页面的url每一页

    :param keyword:
    :param position:
    :return: response
    """

    search_url = 'http://www.dianping.com/search/keyword/193/0_{}/p{}'
    for i in count(1):
        current_url = search_url.format(quote(keyword), str(i))
        response = spider.get(current_url)
        if '检查关键词填写是否有误' in response.text:
            return None
        else:
            yield response


def shop_page_generator(keyword: str, position: str) -> list:
    """生成店铺页面url

    :param keyword:
    :param position: 地点
    :return: url like http://www.dianping.com/shop/l9ZszA41xUchPAwb
    """
    for search_page in search(keyword, position):
        # 解析获得 'http://www.dianping.com/shop/l9ZszA41xUchPAwb'等url
        ul = search_page.xpath("//div[@id='shop-all-list']//ul")
        for li in ul[0]:
            a: HtmlElement = li.xpath(".//a")[0]
            # logger.debug('attrib:{}', a.attrib)
            yield a.attrib['href']


def main():
    # 初始化数据库
    if not db.is_connection_usable():
        db.connect()
    if not db.table_exists(Shop):
        db.create_tables([Shop])
    if not db.table_exists(Comment):
        db.create_tables([Comment])

    keyword = input('input keyword(输入新疆来测试): ')
    position = input('input position(随便输入): ')

    for search_url in shop_page_generator(keyword, position):
        '''search_url == *
        [
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        'http://www.dianping.com/shop/l9ZszA41xUchPAwb',
        ]
        '''
        logger.info('正在解析: {}', search_url)
        # 解析保存数据
        parse_info(search_url)


def test_request():
    r = spider.get('http://www.dianping.com/shop/l9ZszA41xUchPAwb', cache=Spider.DISABLE_CACHE)
    logger.info(r.__repr__())
    print(r.text)


if __name__ == '__main__':
    exit(main())
