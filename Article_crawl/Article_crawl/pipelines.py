# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import MySQLdb
import MySQLdb.cursors

from twisted.enterprise import adbapi


class ArticleCrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):

    def __init__(self):

        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'Panyanqi1203@$', 'scrapy_data',
                                    charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql, params = item.get_insert_sql()
        self.cursor.execute(insert_sql, params)
        self.conn.commit()


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(host=settings['MYSQL_HOST'], db=settings['MYSQL_DATABASE'], user=settings['MYSQL_USER'],
                        passwd=settings['MYSQL_PASSWORD'], charset='utf8', use_unicode=True,
                        cursorclass=MySQLdb.cursors.DictCursor,)
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        print('Start insert')
        cursor.execute(insert_sql, params)
