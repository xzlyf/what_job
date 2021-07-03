import requests

'''
https://www.liepin.com/
待完成
'''


class Liepin:
    __headers = {
        'user-agent': "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
        'cache-control': "no-cache",
        'referer': 'https://www.zhipin.com/?ka=header-home'

    }

    def __init__(self, keyword):
        self.keyword = keyword

    # 显示当前关键字
    def show_keyword(self):
        print(self.keyword)

    def do_it(self):
        response = requests.get(
            "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=&d_ckId=&d_sfrom=search_fp&d_curPage=0&d_pageSize=40&siTag=&key=android",
            headers=self.__headers)
        with open("./cache/cc.html", "w+", encoding="utf-8") as f:
            f.write(response.text)
