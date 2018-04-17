import tools
if __name__ == '__main__':
    ArticleList = [0,1,2,3,4]
    NextUrlDict = {}
    # for i in range(len(ArticleList) - 1):
    #     print(i, ArticleList[i+1])
    #     key = ArticleList[i] * ArticleList[i]
    #     NextUrlDict[key] = ArticleList[i+1]
    # print(ArticleList)
    # print(NextUrlDict)
    NextUrlDict["name"] = "Tom"
    name = None
    if name in NextUrlDict:
        print(NextUrlDict[name])
    else:
        print("不存在")