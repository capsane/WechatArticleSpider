# -*- coding:utf8 -*-

import requests
import time
import random
import json
import re
from bs4 import BeautifulSoup
import get_biz
import PublishArticle as dart


def get_read_like_num():

    return 0, 0


def get_article_content(html):
    # <div class="rich_media_content " id="js_content">
    bs = BeautifulSoup(open("article_content", encoding="utf-8"), "html.parser")
    # bs = BeautifulSoup(html, "html.parser")
    script = bs.find(name="div", attrs={"class": "rich_media_content"})
    content = script.text
    return content


if __name__ == '__main__':
    content = get_article_content("")
    print(content)
