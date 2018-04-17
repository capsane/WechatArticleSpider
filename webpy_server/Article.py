# -*- coding:utf8 -*-
import re


class Article:
    # 只分析49图文
    type = 49
    # 从公众号历史文章传递进来
    biz = ""
    nickname = ""
    datetime = 0
    standardtime = ""

    # raw_dict中提取
    idx = 0           # 第几栏, 还是要由url获取
    title = ""
    author = ""
    content_url = ""    # 文章详情url，其中包含biz, index
    digest = ""         # 摘要
    copyright_stat = 0    # TODO:可能是：11表示原创
    mid = ""
    article_id = ""

    # 待提取
    subtype = 9
    cover = ""          # 封面url
    del_flag = 0            # 未知

    content = ""            # 构造的时候未知，读取文章详细信息的时候提取
    read_num = 0            # 构造的时候未知
    like_num = 0            # 构造的时候未知

    # isOriginal = False    # 需要文章内容中提取

    def __init__(self, raw_dict, biz, nickname, datetime, standardtime):
        # initial
        self.content_url = ""
        self.copyright_stat = 0
        self.digest = ""
        self.del_flag = 0  # 未知
        self.mid = ""
        self.article_id = ""

        if raw_dict:
            # 通过公众号历史文章传递
            self.biz = biz
            self.nickname = nickname
            self.datetime = datetime
            self.standardtime = standardtime

            # 提取得到部分文章信息
            # 判断是否删除
            # if 'content_url' not in raw_dict.keys():
            if not raw_dict['content_url'].strip():
                self.del_flag = 1
            else:
                self.del_flag = 0
                self.author = raw_dict['author']
                self.content_url = raw_dict['content_url'].replace("\\", "")
                self.title = raw_dict['title']
                self.copyright_stat = raw_dict['copyright_stat']
                if 'digest' in raw_dict:
                    self.digest = raw_dict['digest']
                else:
                    print("Warning: raw_dict has no key named digest!")
                # self.del_flag = raw_dict['del_flag']
                # self.del_flag = 0    # 自定义删除标志
                # 从content_url中提取idx
                self.extract_biz_index()
        else:
            print("Error: Article: The input of multi_app_msg_item is None !!!")

    def extract_biz_index(self):
        url = self.content_url
        if not url:
            print("Article: The url of the article is None !!!")
        else:
            biz = re.search("_biz=.*?==", url).group()[5:]
            if biz != self.biz:
                print("Error: 历史文章biz != 文章url中的biz！")
            idx = re.search("idx=.*?&", url).group()[4:-1]
            self.idx = int(idx)

    # 阅读量和点赞量需要获取每篇文章的详情之后才能获取到
    def set_read_num(self, read_num):
        self.read_num = read_num

    def set_like_num(self, like_num):
        self.like_num = like_num

    # JSON化，用于入库
    def json(self):
        return {
            "biz": self.biz,
            "nickname": self.nickname,
            "idx": self.idx,
            "title": self.title,
            "author": self.author,
            "type": self.type,
            "content_url": self.content_url,
            "digest": self.digest,
            "datetime": self.datetime,
            "时间": self.standardtime,
            "read_num": self.read_num,
            "like_num": self.like_num,
            "del_flag": self.del_flag,
            "content": self.content,
            "copyright_stat": self.copyright_stat,
            "mid": self.mid,
            "article_id": self.article_id
        }


if __name__ == '__main__':
    # url111 = 'http://mp.weixin.qq.com/s?__biz=MjM5MzI5NzQ1MA==&mid=2654644844&idx=1&sn=a5ae8ec3d6a9daefb4fe45c62bffa5e6&chksm=bd572f298a20a63fedf55536ca1da53a225f2c8d1b0b47d0ef0c59ff3eb4fea1d04d9b160618&scene=27#wechat_redirect'
    # biz = re.search("_biz=.*?==", url111).group()[5:]
    # idx = re.search("idx=.*?&", url111).group()[4:-1]
    # print(biz)
    # print(idx)
    # a = []
    # a.append(1)
    # a.append(2)
    # print(a.__len__())
    # pass
    a = "http:\/\/www.baidu.com"
    b = a.replace("\\", "")
    print(a)
    print(b)
