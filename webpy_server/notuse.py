import tools
if __name__ == '__main__':
    ArticleList = [0,1,2,3,4]
    NextUrlDict = {}
    # for i in range(len(ArticleUrlList) - 1):
    #     print(i, ArticleUrlList[i+1])
    #     key = ArticleUrlList[i] * ArticleUrlList[i]
    #     NextUrlDict[key] = ArticleUrlList[i+1]
    # print(ArticleUrlList)
    # print(NextUrlDict)
    NextUrlDict["name"] = "Tom"
    name = None
    if name in NextUrlDict:
        print(NextUrlDict[name])
    else:
        print("不存在")