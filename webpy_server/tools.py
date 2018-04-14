from mongodb import MongoDB
from queue import Queue
from get_biz import read_lines_from_file


def init_account_queue():
    # 新氧，唐唐，十点读书，新华社
    # AccountQueue.put("MjM5OTIwNjQxNw==")
    # AccountQueue.put("MjM5OTIwODMzMQ==")
    # AccountQueue.put("MjM5MDMyMzg2MA==")
    # AccountQueue.put("MzA4NDI3NjcyNA==")
    triples = read_lines_from_file("公众号result_pre.txt")
    # biz,nickname,name
    for line in triples:
        biz_name = line.split(',')
        TotalAccount.append(biz_name)
    print("Initial TotalAccount List size: %d" % len(TotalAccount))
    # TODO:
    for i in range(2):
        AccountQueue.put(TotalAccount[i])


# FIXME: 如何正确的初始化
print("import tools: Queue和MongoDB初始化")

TotalAccount = []
AccountQueue = Queue()
NextArticleUrlQueue = Queue()
RealArticleQueue = Queue()
mongodb = MongoDB()
TempArticle = None
INDEX = 1
init_account_queue()




