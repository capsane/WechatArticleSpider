# -*- coding:utf8 -*-

import requests
import time
import random
import json
import re
from bs4 import BeautifulSoup
import get_biz
import PublishArticle as dart


# 暂时可以忽略
cookie = "rewardsn=; wxuin=3678518974; devicetype=android-17; version=26060533; lang=zh_CN; wxtokenkey=777; " \
         "pass_ticket=DibB1nDpBpGg/rL82fN4vz+NY/uC/1910CUFLVhLppUjoOAsdaFU40/8/c6eU003; " \
         "wap_sid2=CL79htoNElx5bEpIQXJqUDVKd1Zza1JpM1p2eUVjeUNCZXJMd2x2WnVHdlE0UWpNSTBHbklKa3VvYndmSjNLbl8yNHJoSGc3dkVtS1JHSmUwZ25LMTBsNWc3MGgyTFlEQUFBfjDakIbWBTgNQJVO; "

headers = {
    "Host": "mp.weixin.qq.com",
    "Connection": "keep-alive",
    "X-WECHAT-UIN": "MzY3ODUxODk3NA%3D%3D",
    "X-WECHAT-KEY": "74bcb85e2727479c1ec01f410b63d124c3a1af8abbc210f545a56f0e3c7e919506fc7fc1e507f6a5db8e40f423eade10ce594b604f168627489bbc5bfb677e1857b928781c2ca0f304ba5f0220233ce2",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "X-Requested-With": "com.tencent.mm",
    "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; SCH-I919U Build/JDQ39E) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30 MicroMessenger/6.6.5.1280(0x26060533) NetType/WIFI Language/zh_CN",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN, en-US",
    "Accept-Charset": "utf-8, iso-8859-1, utf-16, *;q=0.7",
    "Cookie": cookie
}

url_pre = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz="
url_post = "&scene=124#wechat_redirect"

names = []
bizs = []


def get_html_by_biz(biz):
    # url = "https://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MjM5Njc3NjM4MA==&devicetype=android-17&version=26060533&lang=zh_CN&nettype=WIFI&ascene=3&pass_ticket=DibB1nDpBpGg%2FrL82fN4vz%2BNY%2FuC%2F1910CUFLVhLppUjoOAsdaFU40%2F8%2Fc6eU003&wx_header=1"
    url = url_pre + biz + url_post
    # url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MTg1ODI1NA==&scene=124&devicetype=iOS11.2.5&version=16060323&lang=en&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=Ih93pI6o%2B88hvER4xVmbvidH6jnRZ2Paz9tsJSLfrVe3u7EJ6UP5claYmLdQORvy&wx_header=1"
    # url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5OTIwNjQxNw==&scene=124&devicetype=iOS11.2.5&version=16060323&lang=en&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=DibB1nDpBpGg/rL82fN4vz+NY/uC/1910CUFLVhLppUjoOAsdaFU40/8/c6eU003&wx_header=1"
    # url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5Njc3NjM4MA==&scene=124&devicetype=android-17&version=26060533&lang=zh_CN&nettype=WIFI&a8scene=3&pass_ticket=DibB1nDpBpGg%2FrL82fN4vz%2BNY%2FuC%2F1910CUFLVhLppUjoOAsdaFU40%2F8%2Fc6eU003&wx_header=1"
    response = requests.get(url=url, headers=headers)
    # 保存HTML到文件
    # fo = open(biz, "w", encoding='utf-8')
    # fo.write(r.text)
    # fo.close()
    html = response.text
    return response.text


# 解析公众号历史文章
def get_history_list(html):
    msg_dict = None
    biz = None
    can_msg_continue = None
    nickname = None
    is_subscribed = None
    # 从文件读取HTML
    # bs = BeautifulSoup(open("迁移", encoding="utf-8"), "html.parser")
    bs = BeautifulSoup(html, "html.parser")
    # 查找 type属性为text/javascript && tag名称为script && 字符串内容中包含"var msgList"的<script>Tag
    script = bs.find(name="script", attrs={"type": "text/javascript"}, text=re.compile("var msgList"))
    if not script:
        # FIXME: 公众号迁移
        print("Error: when get the history list of this html: \n %s\n\n " % html)
        return [], "biz", "can_msg_continue", "nickname", "is_subscribed"
    content = script.text
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        # get recent 10 days articles
        if re.match("var msgList", line):
            msg_list = re.search("{.*}", line).group()
            msg_list = msg_list.replace("&quot;", "\"").replace("&amp;", "&").replace("&amp;", "&").\
                replace("&nbsp;", " ")
            # 公众号历史文章信息字典
            msg_dict = json.loads(msg_list)
            break
        # get the biz
        elif re.match("var __biz", line):
            biz = line.split('\"')[1]
        elif re.match("var can_msg_continue", line):
            can_msg_continue = line.split('=')[1].split('*')[0]
        elif re.match("var nickname", line):
            nickname = line.split('\"')[1]
        elif re.match("var is_subscribed", line):
            is_subscribed = line.split('=')[1].split('*')[0]

            # var can_msg_continue = '1' * 1;
            # var
            # headimg = "http://wx.qlogo.cn/mmhead/Q3auHgzwzM58Frfaic1TBsibCNBiapHWzzodTm9vSqVL2nZ973e0hqYqw/0" | | "";
            # var nickname = "HUGO" | | "";
            # var is_banned = "0" * 1;
            # var __biz = "MjM5MzI5NzQ1MA==";
            # var next_offset = "10" * 1;

    # 返回近十天的历史文章列表
    return msg_dict['list'], biz, can_msg_continue, nickname, is_subscribed


# 解析文章内容
def get_article_content(html):
    # <div class="rich_media_content " id="js_content">
    # bs = BeautifulSoup(open("noscript", encoding="utf-8"), "html.parser")
    bs = BeautifulSoup(html, "html.parser")
    script = bs.find(name="div", attrs={"class": "rich_media_content"})
    if script:
        content = script.text
    else:
        content = ""
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!查找文章内容，<script>为空: get_info.py 113 !!!!!!!!!!!!!!!!!!!!!!!!!!")
    return content


if __name__ == '__main__':
    # raw_dict_list, biz, can_message_continue, nickname, is_subscribed = get_history_list("")
    # length = raw_dict_list.__len__()
    # print(length)
    # print(biz)
    # print(can_message_continue)
    # print(nickname)
    # daily_articles = dart.PublishArticle(biz=bizs[3], nickname=names[3], raw_dict=raw_dict_list[0])
    # print(daily_articles.type)
    # print(daily_articles.datetime)
    get_article_content("")
    # get_history_list("")