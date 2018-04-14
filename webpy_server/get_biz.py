# -*- coding:utf8 -*-

import requests
import random
import time
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


NAMES = []


# 清博使用request.get获取
def get_biz_cookie(name):
    # sleep 3
    time.sleep(3)
    biz = ""
    nickname = ""
    url = "http://www.gsdata.cn/query/wx?q="+name
    cookie = "bdshare_firstime=1522394312301; acw_tc=AQAAAGNfbmmHGg0Aw9vMb037nC036xBZ; _csrf-frontend=1dcbc8b29bd8141757ca062ff538f394f91a604c968a2e0356e8607b8d88f605a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%225jLN4NmHiyYU0mmNMmpSl82DLSa6eyGh%22%3B%7D; Hm_lvt_293b2731d4897253b117bb45d9bb7023=1522064255,1522394309,1522403335,1522506280; _gsdataCL=WyIxMjEwMDIiLCIxNTYxMTUzMzc3NiIsIjIwMTgwMzMxMjIyNDUyIiwiMWZkNzE3ZTJjYjEyZTk2MGVjYThmY2NmNGVjNjNiOGIiLDk3NDI4XQ%3D%3D; PHPSESSID=qhq4qqce7non5f0045dcbtjgm7; _identity-frontend=3c96cbe59e07d6bfac88b77c83fe9af11afd2242dc10460faa77882df8b0561da%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22_identity-frontend%22%3Bi%3A1%3Bs%3A26%3A%22%5B%22121002%22%2C%22test+key%22%2C3600%5D%22%3B%7D; Hm_lpvt_293b2731d4897253b117bb45d9bb7023=1522506307"
    headers = {
        "Host": "www.gsdata.cn",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "http://www.gsdata.cn/query/wx?q=hugo",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": cookie
    }

    r = requests.get(url, headers=headers)
    bsObj = BeautifulSoup(r.text, "html.parser")
    # 解析biz：<input type="hidden" class="biz" value="MjM5MzI5NzQ1MA==">
    tagBiz = bsObj.find(name='input', attrs={"class": "biz"})
    if not tagBiz:
        return biz, name
    biz = tagBiz['value']
    # 解析nickname:
    # 1. <a target="_blank" id="nickname" href="/rank/wxdetail?wxname=bQWBlDjScJmq9iondgW5d2v1">HUGO</a>
    # 2. <a target="_blank" id="nickname" href="/rank/wxdetail?wxname=bQWBlDjScJmq9iondgW5d2v1"><span class="color-pink">HUGO</span></a>
    tagName = bsObj.find(name='a', attrs={"target": "_blank", "id": "nickname"})
    if not tagName:
        print("%s has no tagName???????????????????" % biz)
        # print(r.text)
        return biz, nickname
    nickname = tagName.text         # 返回所有的内容？包括子节点的？
    # nickname = tagName.string     # 如果只有一个子节点，便返回子节点的内容
    return biz, nickname


# biz
def readBizs(filename):
    biz_list = []
    fo = open(filename, "r", encoding='utf-8')
    lines = fo.readlines()
    for line in lines:
        biz_list.append(line.split(",")[0])
    fo.close()
    return biz_list


#  read lines from file
def read_lines_from_file(filename):
    fo = open(filename, 'r', encoding='utf-8')
    initial_names = fo.readlines()
    fo.close()
    return initial_names


# biz, nickname, name
def save_initial_biz(names, filename):
    result = []
    for name in names:
        if name == '\n':
            continue
        # 去掉末尾的换行符
        name = name.replace('\n', '').strip()
        biz, nickname = get_biz_cookie(name)
        result.append([biz, nickname, name])
        print("%d: %s, nickname:%s, name:%s" % (len(result), biz, nickname, name))

    # save raw, precise, not found
    f_r = open(filename+"_raw.txt", 'w', encoding="utf-8")
    f_p = open(filename+"_pre.txt", 'w', encoding="utf-8")
    f_nf = open(filename+"_not_found.txt", 'w', encoding="utf-8")
    f_ne = open(filename+"_not_equal.txt", 'w', encoding="utf-8")
    try:
        for account in result:
            f_r.write(account[0]+","+account[1]+","+account[2] + "\n")
            if not account[0]:  # not found
                f_nf.write(account[0]+","+account[1]+","+account[2] + "\n")
            elif account[1] == account[2]:  # precise
                f_p.write(account[0]+","+account[1]+","+account[2] + "\n")
            else:   # not equal
                f_ne.write(account[0]+","+account[1]+","+account[2] + "\n")

        print("save all done.")
    except Exception as e:
        print(e)
    finally:
        f_r.close()
        f_p.close()
        f_ne.close()
        f_nf.close()


def find_redundant_line(lines):
    print("输入中重复的name: %d" % (len(lines) - len(set(lines))))
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)
        else:
            print(line)


if __name__ == '__main__':
    # total_names = read_initial_name("公众号.txt")
    # unique = set(total_names)
    # print("输入中重复的name: %d" % (len(total_names)-len(unique)))
    # save_initial_biz(total_names, "公众号result")

    total_lines = read_lines_from_file(" ")
    find_redundant_line(total_lines)

