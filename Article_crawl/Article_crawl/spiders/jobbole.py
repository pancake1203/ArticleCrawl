# -*- coding: utf-8 -*-
import scrapy

from Article_crawl.items import JobboleItem
from Article_crawl.utils.common import get_md5
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 抓取所有文章的url, 并将文章url叫给下载器（含lead_img_url)
        3. 实现自动翻页
        :param response:
        :return:
        """
        print('>>>def parse')
        if response.status == 404:
            print('>>>>404 Occur, Done')

        # 抓取每篇文章的url，并交给下载器
        post_nodes = response.css('#archive .post.floated-thumb')
        for post_node in post_nodes:
            post_url = post_node.css('.post-thumb a::attr(href)').extract_first()
            lead_img_url = post_node.css('.post-thumb a img::attr(src)').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={'lead_img_url': lead_img_url}, callback=self.parse_detail)

        # 实现自动翻页
        # next_page_url = response.css('a.next.page-numbers::attr(href)').extract_first()
        # if next_page_url:
        #     yield Request(url=parse.urljoin(response.url, next_page_url), callback=self.parse)
        # else:
        #     print('>>>>Crawl finish.')

    def parse_detail(self, response):
        """
        1. 用LoaderItem读取每一页的数据
        2. 将数据yield到Pipeline
        :param response:
        :return:
        """
        print('>>>def parse_detail')
        article_item = JobboleItem()

        # 通过ItemLoader来加载文章内容
        # title = scrapy.Field()
        # post_url = scrapy.Field()
        # lead_img = scrapy.Field()
        # lead_img_url = scrapy.Field()
        # create_date = scrapy.Field()
        # tags = scrapy.Field()
        # original_author = scrapy.Field()
        # original_source = scrapy.Field()
        # content = scrapy.Field()
        # favor = scrapy.Field()
        # collect = scrapy.Field()
        # comments = scrapy.Field()

        item_loader = ItemLoader(item=JobboleItem(), response=response)

        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('title', '.grid-8 .entry-header h1::text')
        item_loader.add_value('post_url', response.url)
        # item_loader.add_value('lead_img_path', )
        item_loader.add_value('lead_img_url', response.meta.get('lead_img_url', ""))
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('original_author', '.copyright-area a::text')
        item_loader.add_css('original_source', '.copyright-area a::text')
        # item_loader.add_css('content', '.entry p')
        item_loader.add_css('favor', '.vote-post-up h10::text')
        item_loader.add_css('collect', '.bookmark-btn::text')
        item_loader.add_css('comments', 'span.href-style.hide-on-480::text')

        article_item = item_loader.load_item()

        # 将article_item传递到pipeline
        yield article_item
