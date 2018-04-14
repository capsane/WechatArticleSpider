# -*- coding:utf8 -*-

import time
import Article as art


# FIXME: 很多公众号一天可以推文很多次。需要改名为PublishArticle
class PublishArticle:
    # 今天的发布的类型，只统计图文消息：49
    type = 49
    biz = ""
    nickname = ""   # 怎么获取，直接外部设置吧
    # 发布时间，Unix时间戳
    datetime = 0
    # 今天的文章，idx：article
    articles = {}
    standardtime = ""

    def __init__(self, biz="MjM5MzI5NzQ1MA==", nickname="忘记起名字了", raw_dict=None):
        # 别忘了初始化。。。。草
        self.articles = {}
        self.datetime = 0

        self.biz = biz
        self.nickname = nickname
        if raw_dict:
            # 发布时间，发布文章类型
            self.datetime = raw_dict['comm_msg_info']['datetime']
            self.standardtime = self.translate_time(self.datetime)
            self.type = raw_dict['comm_msg_info']['type']
            # 文章信息
            if self.type == 49:
                self.init_articles(raw_dict)
            else:
                print(self.nickname + "在" + self.translate_time(self.datetime) + "未发布图文!")
        else:
            print("Error in new DailyArticles because of None raw_dict...")

    def init_articles(self, raw_dict):
        # 头条
        article_first = art.Article(raw_dict['app_msg_ext_info'], self.biz, self.nickname, self.datetime, self.standardtime)
        # 如果未被删除
        if article_first.del_flag != 1:
            self.articles[article_first.idx] = article_first
        # 分栏文章
        other_dict = raw_dict['app_msg_ext_info']['multi_app_msg_item_list']
        num = raw_dict['app_msg_ext_info']['multi_app_msg_item_list'].__len__()
        i = 0
        while i < num:
            article = art.Article(other_dict[i], self.biz, self.nickname, self.datetime, self.standardtime)
            if article.del_flag != 1:
                self.articles[article.idx] = article
            i += 1

    def translate_time(self, timestamp):
        time_local = time.localtime(timestamp)
        time_standard = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        return time_standard

    def get_first_article(self):
        return self.articles[1]
