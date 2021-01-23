"""
general_template
"""
import configparser

import requests
import re
import logging
from itertools import count
from typing import List
from urllib.parse import quote

from peewee import *
from fake_useragent import UserAgent
from lxml.html import HtmlElement

from lazy_spider import utils
from lazy_spider import ResourceRoot
from lazy_spider import Spider

spider = Spider()
logger = logging.getLogger('spider')
res = ResourceRoot('resources')
db = SqliteDatabase('db.sqlite')


def get_header_generator(referer='http://www.dianping.com/beijing/'):
    # 动态改变 referer
    def warp():
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Host': 'www.dianping.com',
            'Referer': referer,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': str(UserAgent().random),
        }
        return header

    return warp


def response_pipeline(s: Spider, response: Spider.Response):
    # 动态修改referer
    s.set_header_generator(get_header_generator(referer=response.url))
    while response.title == '验证中心':
        input('去验证然后回车: {}'.format(response.url))
        response = spider.get(response.history[0].url, cache=Spider.DISABLE_CACHE)
    return response


# 设置爬虫
spider.headers_generator = get_header_generator()
# 让它去打开浏览器验证
spider.response_pipeline = response_pipeline

# 取消每次请求间隔时间
spider.set_sleeper(utils.random_sleeper(0, 8))

# get font mapping
from lazy_spider.parse.fonttools import BaiduORCFontMapping

config = configparser.ConfigParser()
config.read('./config.ini')

# read config
app_id = config.get('BaiduORC', 'AppID')
api_key = config.get('BaiduORC', 'APIKey')
secret_key = config.get('BaiduORC', 'SecretKey')

fm_num = BaiduORCFontMapping(app_id, api_key, secret_key)
fm_address = BaiduORCFontMapping(app_id, api_key, secret_key)
old_css_urls = set()


def get_font_file_url(css_url: str, classname: str) -> str:
    css_resp = spider.get(css_url)
    font_file_url = 'http:' + re.findall('.+url\("(.+.woff)"\);} \.%s' % classname, css_resp.text)[0]
    logger.info(font_file_url, classname)
    return font_file_url


def download_font_file(font_url: str) -> str:
    font_file = spider.get(font_url)
    font_filename = "fonts/%s" % font_url[-13:]
    with open(font_filename, 'wb') as f:
        f.write(font_file.content)
    return font_filename


def update_mapping(css_url):
    if css_url not in old_css_urls:
        fm_num.update(download_font_file(get_font_file_url(css_url, 'num')), show_img=True, strict=True)
        fm_address.update(download_font_file(get_font_file_url(css_url, 'address')), fontsize=45, show_img=True,
                          strict=True)
        old_css_urls.add(css_url)
    return


class Shop(Model):
    url = CharField()
    name = CharField()
    comment_count = IntegerField(null=True)
    avg_price = FloatField(null=True)
    # 口味
    taste = FloatField(null=True)
    # 环境
    environment = FloatField(null=True)
    # 服务
    service = FloatField(null=True)
    # 位置
    position = CharField(null=True)
    tel = CharField(null=True)
    data = TextField(null=True)

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

    # resp = spider.get(url, cache=Spider.DISABLE_CACHE)  # 关闭缓存
    resp = spider.get(url)
    # css文件的url
    css_url = 'http:' + resp.xpath("/html/head/link[10]/@href")[0]
    update_mapping(css_url)

    # 商店名
    shop_name = resp.title[resp.title.find('【') + 1:resp.title.find('】')]

    brief_info = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/div[1]')[0]
    # 星星数
    star_num = int(brief_info.xpath('./span[1]/@class')[0][-2:]) / 10
    # 评论数
    comment_count = ''.join(brief_info.xpath('./span[@id="reviewCount"]/text()|./span[@id="reviewCount"]/d/text()'))
    # 平均价格
    avg_price = ''.join(brief_info.xpath('./span[@id="avgPriceTitle"]/text()|./span[@id="avgPriceTitle"]/d/text()'))

    comment_score = brief_info.xpath('./span[@id="comment_score"]')[0]
    # 口味
    taste = ''.join(comment_score.xpath('./span[1]/text()|./span[1]/d/text()'))
    # 环境
    environment = ''.join(comment_score.xpath('./span[2]/text()|./span[2]/d/text()'))
    # 服务
    service = ''.join(comment_score.xpath('./span[3]/text()|./span[3]/d/text()'))

    expand_info = resp.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]')[0]
    # 地址
    position = ''.join(expand_info.xpath('./div/span/text()|./div/span/e/text()'))
    # 电话
    tel = ''.join(resp.xpath('/html/body/div[2]/div/div[2]/div[1]/p')[0].xpath('./text()|./*/text()'))

    '''清理数据'''
    # comment_count
    try:
        temp = comment_count.replace('条评价', '').strip()
        temp = fm_num.mapping(temp)
        comment_count = int(temp)
    except ValueError:
        comment_count = None

    # service
    try:
        temp = service.replace('服务:', '').strip()
        temp = fm_num.mapping(temp)
        service = float(temp)
    except ValueError:
        service = None

    # taste
    try:
        temp = taste.replace('口味:', '').strip()
        temp = fm_num.mapping(temp)
        taste = float(temp)
    except ValueError:
        taste = None

    # avg_price
    try:
        temp = avg_price.replace('人均:', '').strip()
        temp = fm_num.mapping(temp)
        avg_price = float(temp)
    except ValueError:
        avg_price = None

    try:
        temp = environment.replace('环境:', '').strip()
        temp = fm_num.mapping(temp)
        environment = float(temp)
    except ValueError:
        environment = None

    position = fm_address.mapping(position).strip()
    tel = fm_num.mapping(tel).replace('电话： ', '').strip()

    # todo 星星数目
    # try:
    #     temp = float(taste.replace('口味:', '').strip())
    #     taste = temp
    # except ValueError:
    #     taste = None

    print(shop_name, star_num, comment_count, avg_price, taste, environment, service, position, tel)

    '''暂时不包装到数据库'''
    # 包装 Shop
    query = Shop.select().where(Shop.name == shop_name)
    if not query:
        shop = Shop()
    else:
        shop = Shop()
    shop.url = url
    shop.name = shop_name
    shop.comment_count = comment_count
    shop.avg_price = avg_price
    shop.taste = taste
    shop.environment = environment
    shop.service = service
    shop.position = position
    shop.tel = tel
    shop.data = 'data'
    # 包装评论
    # comments = parse_comment(resp)
    # for comment in comments:
    #     comment.save()

    # 在包装后
    shop.save()


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

    # keyword = input('input keyword(输入新疆来测试): ')
    # position = input('input position(随便输入): ')
    keyword = '黑潮'
    position = '1'

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
