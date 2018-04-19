import time


def get_param(url, key):
    if url == '':
        return None
    url = url.replace('__', '')      # __biz替换为biz
    params = url.split('?')[-1].split('&')
    for param in params:
        key_value = param.split('=', 1)     # TODO: 参数1的含义
        if key == key_value[0]:
            return key_value[1]
    return None


def get_article_id(url):
    url = url.replace('__', '')      # __biz替换为biz
    biz = get_param(url, 'biz')
    mid = get_param(url, 'mid')
    idx = get_param(url, 'idx')
    if not biz or not mid or not idx:
        return None
    return biz+':'+mid+':'+idx


def log_file(filename, line):
    fo = open(filename, 'a', encoding="utf-8")
    log_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    try:
        fo.write(log_time + "   " + line + "\n")
    except Exception as e:
        print(e)
    finally:
        fo.close()


if __name__ == '__main__':
    url = "mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA5NjQ2NTQ4MQ==&scene=124&devicetype=android-17&version=26060536&lang=zh_CN&nettype=WIFI&a8scene=3&pass_ticket=7jhHpB0TwqEBLwHTUWR3lUtcK4GllRxeEtd5gyaDu7jTujAfb%2B6Pf6Pu5IWqeh40&wx_header=1"
    url2 = "mp.weixin.qq.com/s?__biz=MzIxNTkyMDQwNg==&mid=2247491738&idx=1&sn=4bf7159cefe25d026045d801720c3b73&chksm=97925ae3a0e5d3f5ce5ff091b55b19da5eeed0acbc7e82c5d37d7e5d4cb61848ff3425014182&scene=27&ascene=3"
    biz = get_param(url2, "biz")
    id = get_article_id(url2)
    print(biz)
    print(id)
