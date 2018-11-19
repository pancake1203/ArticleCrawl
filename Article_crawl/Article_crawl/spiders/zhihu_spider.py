# -*- coding: utf-8 -*-
import scrapy

import time
import pickle
import re
import json
import datetime
import requests

from scrapy.loader import ItemLoader
from urllib import parse
from selenium import webdriver
from items import ZhihuAnswerItem, ZhihuQuestionItem


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    personal_setting_url = 'https://www.zhihu.com/settings/account'
    answer_start_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&sort_by=default"

    headers= {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "COOKIES_ENABLED": True
    }

    def start_requests(self):
        """
        1. selenium登陆知乎
        2. 保存cookies
        """

        browser = webdriver.Chrome(executable_path='F:\Python\software\chrome6.0\chromedriver')
        browser.get("https://www.zhihu.com/signup?next=%2F")
        tips = browser.find_element_by_css_selector('.SignContainer-switch span').text
        if tips == '登录':
            browser.find_element_by_css_selector('.SignContainer-switch span').click()
        browser.find_element_by_css_selector("div.SignFlow-accountInputContainer input[name='username']").send_keys('username')
        browser.find_element_by_css_selector("div.SignFlow-password input[name='password']").send_keys('password')
        browser.find_element_by_css_selector("div.Login-content button.SignFlow-submitButton").click()

        time.sleep(5)
        cookies = browser.get_cookies()
        cookie_dict = {}

        for cookie in cookies:
            f = open('./Article_crawl/Cookies/zhihu/'+cookie['name']+'zhihu', 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.personal_setting_url, cookies=cookie_dict, meta={'cookie_dict': cookie_dict},
                               dont_filter=True, headers=self.headers, callback=self.if_login)]

    # 检查登陆状态
    def if_login(self, response):
        if response.status == 200:
            print('Login Successfully.')
            cookie_dict = response.meta['cookie_dict']
            yield scrapy.Request(url=self.start_urls[0], headers=self.headers, cookies=cookie_dict)
        else:
            print('Login Failed')


    def parse(self, response):
        """
        1. 获取所有问题url并提交到下载器
        2. 翻页功能
        """

        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https://www.zhihu.com") else False, all_urls)
        all_urls = filter(lambda x: False if x == "https://www.zhihu.com" or x == "https://www.zhihu.com/" else True, all_urls)

        for url in all_urls:
            match = re.match("(.*/question/?(\d+))(/|$).*", url)
            if match:
                url = match.group(1)
                yield scrapy.Request(url, headers=self.headers, callback=self.parse_question, dont_filter=True)
            else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse, dont_filter=True)
                pass

        # test_url = "https://www.zhihu.com/question/20883020"
        # yield scrapy.Request(test_url, headers=self.headers, callback=self.parse_question, dont_filter=True)


    def parse_question(self, response):
        """
        1. 获取问题详情
        """

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)

        question_id = re.match("(.*zhihu.com/question/?(\d+)).*", response.url).group(2)
        item_loader.add_value('question_id', question_id)
        item_loader.add_value('url', response.url)
        item_loader.add_css('title', 'h1.QuestionHeader-title::text')
        item_loader.add_css('content', '.QuestionRichText.QuestionRichText--expandable span')
        item_loader.add_css('topics', '.QuestionHeader-topics .Tag-content .Popover div::text')
        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css('follow_num', '.QuestionFollowStatus-counts .NumberBoard-itemValue::text')
        item_loader.add_css('browse_num', '.QuestionFollowStatus-counts .NumberBoard-itemValue::text')
        item_loader.add_css('comment_num', ".QuestionHeader-Comment button::text")

        question_item = item_loader.load_item()

        yield question_item
        yield scrapy.Request(self.answer_start_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)

    def parse_answer(self, response):
        """
        1. 获取每条回答的信息
        2. 通过api接口自动获取更多回答
        """

        answer_json = json.loads(response.text)

        is_end = answer_json["paging"]["is_end"]
        next_url = answer_json["paging"]["next"]

        for answer in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item['answer_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer["author"]["id"] if 'id' in answer['author'] else None
            answer_item['author_name'] = answer['author']['name'] if 'name' in answer['author'] else None
            answer_item['content'] = answer['content']
            answer_item['agree_num'] = answer['voteup_count']
            answer_item['comment_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)
