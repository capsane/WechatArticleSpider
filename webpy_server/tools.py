def get_param(url, key):
    if url == '':
        return None
    params = url.split('?')[-1].split('&')
    for param in params:
        key_value = param.split('=', 1)
        if key == key_value[0]:
            return key_value[1]
    return None


def get_id(url):
    url = url.replace('__', '')      # __biz替换为biz
    biz = get_param(url, 'biz')
    mid = get_param(url, 'mid')
    idx = get_param(url, 'idx')
    if not biz or not mid or not idx:
        return None
    return biz+':'+mid+':'+idx
