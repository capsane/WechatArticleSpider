from mongodb import MongoDB
from queue import Queue
from get_biz import read_lines_from_file


def init_account_queue():
    triples = read_lines_from_file("公众号result_pre.txt")
    # biz,nickname,name
    for line in triples:
        biz_name = line.split(',')
        TotalAccount.append(biz_name)
    print("Initial TotalAccount List size: %d" % len(TotalAccount))
    # TODO:
    for i in range(2):
        AccountQueue.put(TotalAccount[i])


INDEX = 1
BatchSize = 4

TotalAccount = []
AccountQueue = Queue()
NextArticleUrlQueue = Queue()
RealArticleQueue = Queue()
mongodb = MongoDB()
init_account_queue()

# capsane
ArticleList = []
NextUrlDict = {}

ArticleDict = {}




