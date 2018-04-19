import time
from mongodb import MongoDB
from queue import Queue
from get_biz import read_lines_from_file


def init_account_queue():
    triples = read_lines_from_file("公众号result_pre.txt")
    # biz,nickname,name
    for line in triples:
        biz_name = line.split(',')
        TotalAccount.append(biz_name)
        LogBizName[biz_name[0]] = biz_name[1]   # 用于log出错的biz -> nickname
    print("Initial TotalAccount List size: %d" % len(TotalAccount))
    # TODO:
    for i in range(2):
        AccountQueue.put(TotalAccount[i])


INDEX = 1
BatchSize = 4
# 默认仅仅提取并更新最近三天的历史文章(可能会少于)
RecentDay = 2

TotalAccount = []
LogBizName = {}
AccountQueue = Queue()
NextArticleUrlQueue = Queue()
RealArticleQueue = Queue()
mongodb = MongoDB()
init_account_queue()

# capsane
ArticleUrlList = []
NextUrlDict = {}
ArticleDict = {}

# 每运行2个小时，休息0.3
RunningSecond = 0
StartTime = time.time()
AccountCount = 0




