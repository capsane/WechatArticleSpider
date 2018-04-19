import web
import json
import time
import random
import tools
import PublishArticle as pubart
from get_info import get_history_list
from get_info import get_article_content
import win_unicode_console

from initial import *

# 解决cmd中打印报错
win_unicode_console.enable()
# FIXME: Bug1 保证顺序：get(js)、post(content)、post(num). 对于post(num)可以在nodejs中delay请求num的请求；
# AccountQueue中必须保证至少有1个biz，否则由于get先于post执行，初始biz在getJS时ArticleQueue是空的


# 文章间隔4-5s
MinDelay = 1000 * 4
MaxDelay = 1000 * 5

# 公众号间隔20-30s
MinAccountSleep = 1000 * 20
MaxAccountSleep = 1000 * 30

# Batch间隔60-120s
MinBatchSleep = 1000 * 60
MaxBatchSleep = 1000 * 60 * 2

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
        params = web.input()
        # TODO: 提取_biz
        # <Storage {'lang': 'zh_CN', 'version': '26060532', 'scene': '27', 'chksm': 'bd1488b88a6301ae88858af7f3ce31eb1b6d9d3020f84840dbef86d4e21f65d613c0a4f5cf6d', 'idx': '1', 'wx_header': '1',
        #  'abtest_cookie': 'AwABAAoACwAMAAkAl4oeAKaKHgA+ix4ASIseAHeLHgCpjB4A4IweAAONHgAFjR4AAAA=', 'mid': '2651076715', 'pass_ticket': 'rqYRw2Y9ByHVA1GhpaXcEDR+XRfFeUdd9YzJ6RP/0pGLrE7WipRxKLVj
        # 5HMZUerF', 'sn': '3a06382baf2db57ec8e4563031f7f98a', 'devicetype': 'android-17', 'nettype': 'WIFI', 'ascene': '3', 'https://mp.weixin.qq.com/s?__biz': 'MjM5Njc3NjM4MA=='}>
        biz = params.biz
        mid = params.mid
        idx = params.idx
        key = biz+':'+mid+':'+idx
        print("key：%s" % key)
        return on_article_js(key)


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
        on_recent_articles(htmlbody, requrl)


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
        on_article_content(htmlbody, requrl)


# read, like num
class ReadLikeNum:
    def GET(self):
        return "Response From Web.py 4 ReadLikeNum."

    def POST(self):
        print("Server: 3 receive post of read_like num...")
        data = web.data().decode(encoding="utf-8")
        data_dict = json.loads(data)
        statistic = data_dict['statistic']
        requrl = data_dict['requrl']
        print("requrl: %s" % requrl)
        on_read_like_num(statistic, requrl)


# 处理文章内容
# TODO: 可以选择先入库
def on_article_content(html, requrl):       # requrl修改，添加了&biz字段
    content = get_article_content(html)
    end = min(60, len(content))
    key = tools.get_article_id(requrl)
    if key in ArticleDict:
        cur_article = ArticleDict[key]
        cur_article.content = content
        print("%s %s %s %s" % (key, cur_article.nickname, cur_article.title, content[:end]))
    else:
        print("重复内容请求: ", ArticleDict.keys())
        # raise RuntimeError("key %s not in Dict when update content." % key)


# TODO:可以在提取到content之后就入库，然后更新，防止num请求pass了
def on_read_like_num(statistic, requrl):    # requrl修改，添加了&biz字段
    mid = tools.get_param(requrl, 'mid')
    key = tools.get_article_id(requrl)
    if not key:
        print("on_read_like_num: 找不到key, requrl: %s 可能已经被缓存" % requrl)
        return

    sta_dict = json.loads(statistic)
    read_num = sta_dict['appmsgstat']['read_num']
    like_num = sta_dict['appmsgstat']['like_num']
    if key in ArticleDict:
        cur_article = ArticleDict[key]
        cur_article.read_num = read_num
        cur_article.like_num = like_num
        cur_article.mid = mid
        cur_article.key = key
        print("%s %s read:%d like:%d" % (key, ArticleDict[key].title, read_num, like_num))
        # remove and send to db
        if not mongodb.add("second", ArticleDict[key].json()):
            print("****************************数据库add失败********************************\n")
        # 删除已经访问num的文章
        del ArticleDict[key]       # req1, req2, num, req3. 对于req3直接pass
        print("ArticleDict.len: %d" % len(ArticleDict))
    else:   # TODO:不存在文章
        print(ArticleDict.keys())
        # raise RuntimeError("key: %s not in Dict when update num." % key)


# 处理历史文章列表
def on_recent_articles(html, requrl):
    history_list, biz, can_message_continue, nickname, is_subscribed = get_history_list(html)
    # 正在/已经迁移或暂时封禁的公众号
    if len(history_list) == 0:
        print("处理历史文章：%s 没有历史文章，可能在迁移ing..." % nickname)
        biz = tools.get_param(requrl, 'biz')
        tools.log_file("ErrorAccount.log", LogBizName[biz] + ":" + biz)
        return

    print("处理历史文章：%s, 推送数量：%d, 更多: %s, 订阅: %s" % (nickname, history_list.__len__(), can_message_continue, is_subscribed))
    # 获取每天的文章
    for raw_dict_of_the_day in history_list:
        # 如果当天发布的不是图文消息，则略过
        if raw_dict_of_the_day['comm_msg_info']['type'] != 49:
            continue
        daily_articles = pubart.PublishArticle(biz=biz, nickname=nickname, raw_dict=raw_dict_of_the_day)
        # RecentDay以内的文章才需要访问(insert/update)
        span = (time.time() - daily_articles.datetime) / 86400
        if span < RecentDay:
            # DailyArticle.articles是一个字典{idx: Article},打印当天文章idx
            print(daily_articles.standardtime, "   文章idx: ", daily_articles.articles.keys())
            for article in daily_articles.articles.values():
                url = article.content_url.replace("\\", "")
                article.content_url = url
                # biz:mid:idx
                key = tools.get_article_id(url)
                article.article_id = key
                # 送入ArticleDict, ArticleUrlList
                ArticleDict[key] = article
                ArticleUrlList.append(url)
                # TODO: 同时初始化NextUrlDict
                last = len(ArticleUrlList)-1
                if last > 0:
                    pre_key = tools.get_article_id(ArticleUrlList[last-1])
                    NextUrlDict[pre_key] = ArticleUrlList[last]
                print("Dict.len=%d, Add %s" % (len(ArticleDict), key))
                print("List.len=%d, Add %s" % (len(ArticleUrlList), url))
                print("NextDict.len=%d" % len(NextUrlDict))


# 处理文章详情
def on_article_js(key):
    if key not in ArticleDict:
        result_js = js_repeat_article(key)
    elif key in NextUrlDict:
        result_js = js_next_article(key)
    else:       # key no in NextUrlDict
        result_js = js_first_account(key)
    return result_js


def on_history_js():
    if not AccountQueue.empty():
        result_js = js_next_account()
    else:
        print("这是最后一个需要处理的history,返回第一篇文章url作为JS, 同时初始化NextUrlDict")
        # id: next_url
        result_js = js_first_article()
    return result_js


def js_next_article(key):
    print("on_article_js: %s" % key)
    next_url = NextUrlDict[key]
    article_url = '\'' + next_url + '\''
    article_js = '<script type="text/javascript">var url =' + article_url + ';setTimeout(function() {window.location.href=url;}, ' + str(random.randint(MinDelay, MaxDelay)) + ');</script>'
    return article_js


# 开始新一轮batch: 1.pre batch没有添加文章; 2.pre batch的最后一篇文章
def js_first_account(key):
    # call from the last article of pre batch, clear the global dict and list
    if key:
        NextUrlDict.clear()
        last_article = ArticleDict[key]         # ArticleDict中只保留key这篇文章，待访问
        ArticleDict.clear()
        ArticleDict[key] = last_article
        ArticleUrlList.clear()

    batch_add_account()
    account_js = batch_first_account_js()
    return account_js


def batch_add_account():
    # Add account to AccountQueue
    for i in range(BatchSize):
        global INDEX
        INDEX = 1 + INDEX
        if INDEX == len(TotalAccount):
            INDEX = 0
        AccountQueue.put(TotalAccount[INDEX])
        print("Index: %d, %s" % (INDEX, TotalAccount[INDEX]))


def batch_first_account_js():
    account_biz = AccountQueue.get()[0]
    # global AccountCount
    # AccountCount += 1
    account_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz='\
                 + account_biz + '&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, ' \
                 + str(random.randint(MinBatchSleep, MaxBatchSleep)) + ');</script>'
    return account_js


# 本轮batch中访问过的文章会从ArticleDict中删除
def js_repeat_article(key):
    print("on_article_js重复: %s" % key)
    # raise RuntimeError("Error")
    # TODO: 对于重复的文章内容请求，return?return js
    return ""


def js_next_account():
    account = AccountQueue.get()
    account_biz = account[0]
    print("You have just get: ", account, "and return its biz as JS.")
    # 封放策略, 访问30个account之后暂停10min
    global AccountCount
    AccountCount += 1
    if AccountCount >= 30:
        AccountCount = 0
        sleep_time = 1000 * 60 * 10
        print("sleep for 10 minutes...")
    else:
        sleep_time = random.randint(MinAccountSleep, MaxAccountSleep)
    account_js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz='\
                 + account_biz + '&scene=124#wechat_redirect";setTimeout(function() {window.location.href=url;}, ' \
                 + str(sleep_time) + ');</script>'
    return account_js


def js_first_article():
    # 初始化NextUrlDict
    # FIXME: 这里是不对的，初始化NextUrlDict忽略了这个返回的文章列表，因为js在解析列表之前，导致只取了前三个历史文章。怎么办，AccountQueue中最后一个acocunt重复一次？
    # FIXME: 如果ArticleList为0
    # NextUrlDict.clear()
    # for i in range(len(ArticleUrlList) - 1):
    #     key = tools.get_article_id(ArticleUrlList[i])
    #     NextUrlDict[key] = ArticleUrlList[i + 1]
    # print("DEBUG: 初始化之后, ArticleUrlList：%s\n NextUrlDict:%s" % (ArticleUrlList, NextUrlDict))

    # 本轮batch的公众号中并没有添加任何文章, 那就继续添加account
    if len(ArticleUrlList) == 0:
        print("本轮batch没有添加任何文章，开始新的一轮batch...")
        return js_first_account(None)
    else:
        article_url = '\'' + ArticleUrlList[0] + '\''
        article_js = '<script type="text/javascript">var url =' + article_url + ';setTimeout(function() {window.location.href=url;}, ' + str(random.randint(MinDelay, MaxDelay)) + ');</script>'
        return article_js


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
