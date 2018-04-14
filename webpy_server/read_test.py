import json


def read():
    fo = open("raw.txt", "r", encoding='utf-8')
    html = fo.readline()
    fo.close()
    dirct = json.loads(html)
    return dirct['htmlbody']


if __name__ == '__main__':
    fo = open("raw.txt", "r", encoding='utf-8')
    html = fo.readline()
    fo.close()
    dirct = json.loads(html)
    print(dirct['htmlbody'])
    print(html)

