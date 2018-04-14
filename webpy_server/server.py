import web
import json
import time
# from mongodb import MongoDB
# from queue import Queue
import PublishArticle as pubart
from get_info import get_history_list
from get_info import get_article_content
import win_unicode_console

from tools import *

# 解决cmd中打印报错
win_unicode_console.enable()
# FIXME: Bug1 保证顺序：get(js)、post(content)、post(num). 对于post(num)可以在nodejs中delay请求num的请求；
# FIXME: Bug2 new a MongoDB.连接到数据库 wechat。：此时也会执行TempArticle = None。 为什么数据库会重连？？，使用单例？。import tools;
# FIXME: bug3 AccountQueue中必须保证至少有1个biz，否则由于get先于post执行，初始biz在getJS时ArticleQueue是空的
# FIXME: Bug4 一篇文章请求两次s?_biz的情况 : 检查
# FIXME: 客户端打开文章详情页的时候，网络卡顿或者延迟崩溃

# TODO: 1 Server2: 提取到的content之后报错，在准备入库之前，但是提取content试了没有问题
# TODO: 2 对于标题和提取到的内容不同步的问题，可以在修改文章内容的时候提取一下title，和TempArticle.title比对一下，num里可能就没有标题
TimeDelay = 1000

urls = (
    '/', 'Index',
    '/history_next', 'HistoryJs',
    '/article_next', 'ArticleJs',
    '/recent', 'RecentArticle',
    '/detail', 'ArticleDetail',
    '/num', 'ReadLikeNum'
)


class Index:
    def GET(self):
        return "Hello, This is the index page!"


# 历史请求JS
class HistoryJs:
    def GET(self):
        print("ServerHistory: receive get from history_next for js...")
        return on_history_js()


# 文章请求JS
class ArticleJs:
    def GET(self):
        print("Server: 1 receive get from article_next for js...")
        return on_article_js()


# 历史文章
class RecentArticle:
    def GET(self):
        return "Response From Web.py 4 RecentArticle."

    def POST(self):
        print("ServerHistory: receive post of recent_article...")
        data = web.data().decode(encoding="utf-8")
        data_dict = json.loads(data)
        htmlbody = data_dict['htmlbody']
        requrl = data_dict['requrl']
        on_recent_articles(htmlbody)


# 文章详情
class ArticleDetail:
    def GET(self):
        return "Response From Web.py 4 ArticleDetail."

    def POST(self):
        print("Server: 2 receive post of article_detail...")
        data = web.data().decode(encoding="utf-8")
        data_dict = json.loads(data)
        htmlbody = data_dict['htmlbody']
        requrl = data_dict['requrl']
        on_article_detail(htmlbody)


# read, like num
class ReadLikeNum:
    def GET(self):
        return "Response From Web.py 4 ReadLikeNum."

    def POST(self):
        print("Server: 3 receive post of read_like num...")
        data = web.data().decode(encoding="utf-8")
        data_dict = json.loads(data)
        statistic = data_dict['statistic']
        on_read_like_num(statistic)


# 处理文章内容
def on_article_detail(html):
    content = get_article_content(html)
    TempArticle.content = content
    end = min(60, len(content))
    print("提取到的content: %s %s" % (TempArticle.title, content[:end]))


# FIXME:处理read, liked, 此时可能还是为None?
def on_read_like_num(statistic):
    sta_dict = json.loads(statistic)
    read = sta_dict['appmsgstat']['read_num']
    like = sta_dict['appmsgstat']['like_num']
    print("read: %d, like: %d" % (read, like))
    TempArticle.read_num = read
    TempArticle.like_num = like
    # 暂且默认read,like获取后，content已经不为空了
    # FIXME:但是说不定content确实就是空呢;为空可能是因为Server没有响应，重开就可以
    # 可以考虑在TempArticle再次赋值的时候保存入库
    if not TempArticle.content.strip():
        # 如果还没有提取到content，sleep(1)，延迟1s入库
        print("++++++++++++++++++++++ read, like之后，文章内容为空， sleep 1s???+++++++++++++++++++++++++++++")
        # FIXME: 主线程阻塞
        # time.sleep(1)   # TODO: 这样就不会bug3了？？？但是Bug1
        if not TempArticle.content.strip():
            print("-------------------------------------content依然为空-----------------------------------------------")
    end = min(60, len(TempArticle.content))
    print("准备入库 %s: Title: %s %s" % (TempArticle.nickname, TempArticle.title, TempArticle.content[:end]))
    if not mongodb.add("article", TempArticle.json()):
        print("****************************数据库add失败********************************")


# 处理历史文章
def on_recent_articles(html):
    history_list, biz, can_message_continue, nickname, is_subscribed = get_history_list(html)
    if len(history_list) == 0:
        print("%s 没有历史文章，可能在迁移ing..." % nickname)
        return
    print("处理历史文章：%s, 推送数量：%d, 更多: %s, 订阅: %s" % (nickname, history_list.__len__(), can_message_continue, is_subscribed))
    # 获取每天的文章
    # FIXME: 公众号迁移
    for raw_dict_of_the_day in history_list:
        # 如果当天发布的不是图文消息，则略过
        if raw_dict_of_the_day['comm_msg_info']['type'] != 49:
            print("Ignore this day %s : none type:49 message..." % raw_dict_of_the_day['comm_msg_info']['datetime'])
            continue
        daily_articles = pubart.PublishArticle(biz=biz, nickname=nickname, raw_dict=raw_dict_of_the_day)
        # TODO:暂时不考虑大规模收集历史数据
        # 三天以内的文章才需要访问(insert, update)
        span = (time.time() - daily_articles.datetime) / 86400
        if span < 2:
            # DailyArticle.articles是一个字典{idx: Article},打印当天文章idx
            print(daily_articles.standardtime, "   文章idx: ", daily_articles.articles.keys())
            for article in daily_articles.articles.values():
                # 将文章入队列
                url = article.content_url.replace("\\", "")
                article.content_url = url
                RealArticleQueue.put(article)
                NextArticleUrlQueue.put(url)
                print("Queue size after put: ", RealArticleQueue.qsize(), NextArticleUrlQueue.qsize(), article.title)


# 处理文章详情
def on_article_js():
    # 完善当前访问的文章的详细信息，此时RealArticle必定不为空
    global TempArticle
    TempArticle = RealArticleQueue.get()
    print("RealArticle size after get: %s" % RealArticleQueue.qsize())

    if not NextArticleUrlQueue.empty():
        # 下一个需要访问的文章url
        next_url = NextArticleUrlQueue.get()
        print("NextArticleUrlQueue size after get: %s" % NextArticleUrlQueue.qsize())
        article_url = '\'' + next_url + '\''
        result_js = '<script type="text/javascript">var url =' + article_url + ';setTimeout(function() {window.location.href=url;}, 1000);</script>'
    else:
        print("NextArticleUrlQueue is empty, add Account..")
        # TODO:一轮结束后，继续添加Account，例如添加2个Account，同时取出第一个Account biz作为JS返回
        for i in range(3):
            global INDEX
            INDEX += 1
            AccountQueue.put(TotalAccount[INDEX])
            print("Index: %d, %s" % (INDEX, TotalAccount[INDEX]))
        account_biz = AccountQueue.get()[0]
        result_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' + account_biz + '&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, 1000);</script>'
    return result_js


def on_history_js_back():
    print("2222222222222222222222222222222222222222222222222根据Queue, 处理需要返回的JS...")
    if not RealArticleQueue.empty():
        global TempArticle
        TempArticle = RealArticleQueue.get()
        print("size after get: ", RealArticleQueue.qsize())
        print("Article.Queue is not empty, get: %s" % TempArticle.title)
        article_url = '\'' + TempArticle.content_url + '\''
        result_js = '<script type="text/javascript">var url =' + article_url + ';setTimeout(function() {window.location.href=url;}, 10000);</script>'
    elif not AccountQueue.empty():
        print("RealArticle is empty, not the AccountQueue, so fetch next Account")
        account_biz = AccountQueue.get()
        result_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' + account_biz + '&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, 10000);</script>'
    else:
        print("AccountQueue is empty, return 唐唐")
        result_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5OTIwODMzMQ==&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, 10000);</script>'
        # default_js = ""
    return result_js


def on_history_js():
    # 取出AccountQueue中的所有公众号的历史文章
    if not AccountQueue.empty():
        account = AccountQueue.get()
        account_biz = account[0]
        print("AccountQueue size after get: %d" % AccountQueue.qsize())
        print("You have just get: ", account, "and return its biz as JS.")
        result_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' + account_biz + '&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, 1000);</script>'
    else:
        # AccountQueue为空时,取出第一个文章url    # FIXME: 如果此时队列里面只有一个文章
        print("AccountQueue is empty, pop the first article url ...")
        next_url = NextArticleUrlQueue.get()
        print("ArticleUrlQueue size after First get: %s" % NextArticleUrlQueue.qsize())
        article_url = '\'' + next_url + '\''
        result_js = '<script type="text/javascript">var url =' + article_url + ';setTimeout(function() {window.location.href=url;}, 1000);</script>'
    return result_js


if __name__ == '__main__':
    app = web.application(urls, globals())
    print("Server is running...")
    app.run()
