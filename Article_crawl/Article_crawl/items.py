# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from datetime import datetime
from Article_crawl.utils import common
from Article_crawl.settings import MYSQL_DATE_FORMAT

# from scrapy.loader import ItemLoader
# from scrapy.loader.processors import TakeFirst


class ArticleCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleItem(scrapy.Item):

    title = scrapy.Field()
    url_object_id = scrapy.Field()
    post_url = scrapy.Field()
    lead_img_path = scrapy.Field()
    lead_img_url = scrapy.Field()
    create_date = scrapy.Field()
    tags = scrapy.Field()
    original_author = scrapy.Field()
    original_source = scrapy.Field()
    content = scrapy.Field()
    favor = scrapy.Field()
    collect = scrapy.Field()
    comments = scrapy.Field()


    def get_insert_sql(self):

        insert_sql = """
                    insert into jobble_article(title, post_url, lead_img_url, create_date, tags,
                    original_author, orginal_source, favor, collect, comments, url_object_id) 
                    values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s) 
                """
        title = self['title'][0]
        url_object_id = self['url_object_id'][0]
        post_url = self['post_url']
        # lead_img_path = scrapy.Field()
        lead_img_url = self['lead_img_url']
        create_date = datetime.strptime(self['create_date'][0].replace('·', "").strip(), MYSQL_DATE_FORMAT)
        tags = "/".join(self['tags'])
        original_author = self['original_author'][0]
        original_source = self['original_source'][1]

        favor = self['favor'][0]
        collect = common.extract_num(self['collect'][0])
        comments = common.extract_num(self['comments'][0])

        params = (title, post_url, lead_img_url, create_date, tags, original_author, original_source,
                  favor, collect, comments, url_object_id)
        return insert_sql, params
