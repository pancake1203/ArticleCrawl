# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime

from utils import common
from settings import MYSQL_DATE_FORMAT, MYSQL_DATETIME_FORMAT

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
        """
        1.sql insert 语句
        2.对itemloader数据进行过滤
        """

        insert_sql = """
                    insert into jobble_article(title, post_url, lead_img_url, create_date, tags,
                    original_author, original_source, favor, collect, comments, url_object_id) 
                    values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s) 
                """

        title = self['title'][0]
        url_object_id = self['url_object_id'][0]
        post_url = self['post_url'][0]
        # lead_img_path = scrapy.Field()
        lead_img_url = self['lead_img_url'][0]
        create_date = datetime.strptime(self['create_date'][0].replace('·', "").strip(), MYSQL_DATE_FORMAT)

        # 若干文章标签会出现 “评论” 字样，对其进行过滤
        tags_list = [element for element in self['tags'] if not element.strip().endswith('评论')]
        tags = "/".join(tags_list)

        # 文章出处
        if len(self['original_author']) == 2:
            original_author = self['original_author'][0]
            original_source = self['original_source'][1]
        elif len(self['original_author']) == 1:
            original_author = self['original_author'][0]
            original_source = ""
        else:
            original_author = ""
            original_source = ""

        # 提取点赞/收藏/评论数
        favor = self['favor'][0]
        collect = common.extract_num(self['collect'][0])
        comments = common.extract_num(self['comments'][0])

        params = (title, post_url, lead_img_url, create_date, tags, original_author, original_source,
                  favor, collect, comments, url_object_id)
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):

    question_id = scrapy.Field()
    url = scrapy.Field()
    topics = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answer_num = scrapy.Field()
    follow_num = scrapy.Field()
    browse_num = scrapy.Field()
    comment_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """
        insert into zhihu_question(question_id,url,topics,title,content,answer_num,follow_num,
        browse_num,comment_num,crawl_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE content=VALUES(content),answer_num=VALUES(answer_num),follow_num=values(follow_num),
        browse_num=VALUES(browse_num),comment_num=VALUES(comment_num),crawl_time=VALUES(crawl_time)
        """

        question_id = self['question_id'][0]
        url = self['url'][0]
        topics = '/'.join(self['topics'])
        title = self['title'][0]
        content = self['content'][0]
        answer_num = common.remove_num_dot(self['answer_num'][0])
        follow_num = common.remove_num_dot(self['follow_num'][0])
        browse_num = common.remove_num_dot(self['browse_num'][1])
        comment_num = common.extract_num(self['comment_num'][0])
        crawl_time = datetime.datetime.now().strftime(MYSQL_DATETIME_FORMAT)

        params = (question_id, url, topics, title, content, answer_num,follow_num, browse_num, comment_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):

    answer_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    author_name = scrapy.Field()
    content = scrapy.Field()
    agree_num = scrapy.Field()
    comment_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
        INSERT INTO zhihu_answer (answer_id, url, question_id, author_id, author_name, content, agree_num, comment_num, create_time, update_time, crawl_time) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE author_name=VALUES(author_name), content=VALUES(content), agree_num=VALUES(agree_num),comment_num=VALUES(comment_num),update_time=values(update_time),crawl_time=VALUES(crawl_time)
        """


        answer_id = str(self['answer_id'])
        url = self['url']
        question_id = self['question_id']
        author_id = self['author_id']
        author_name = self['author_name']
        content = self['content']
        agree_num = self['agree_num']
        comment_num = self['comment_num']
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(MYSQL_DATE_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(MYSQL_DATE_FORMAT)
        crawl_time = datetime.datetime.now().strftime(MYSQL_DATETIME_FORMAT)

        params = (answer_id, url, question_id, author_id, author_name, content, agree_num, comment_num, create_time,
                  update_time, crawl_time)

        return insert_sql, params

