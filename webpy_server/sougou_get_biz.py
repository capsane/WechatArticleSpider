# -*- coding:utf8 -*-

import requests
import random
import time
from bs4 import BeautifulSoup

url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=java&ie=utf8&_sug_=n&_sug_type_="

r = requests.get(url)
bsObj = BeautifulSoup(r.text, "html.parser")