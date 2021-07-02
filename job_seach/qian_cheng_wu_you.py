import json
import pathlib
import time

import requests

"""
xlrd是读excel的库,支持.xls,.xlsx文件的读，
xlwt是写excel的库，支持写.xls文件。
xlutils提供其他功能：如复制一份excel。
"""
import xlwt
from string import Template


class QCheng:
    # 添加请求头
    __headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    '''
    =======参数说明=======
    ${city} = 城市代码（参考get_area_code()返回的数据）
        000000 = 全国热门城市
        
    ${area} = 区代码
        000000 = 所有区
        
    ${keyword} = 关键词
    
    ${page} = 页数，默认一页50条数据
        
    ${workyear} = 工作经验
        99:所有（默认）
        01:在校生/应届
        02:1-3年
        03:3-5年
        04:5-10年
        05:10年以上
        06:无需经验
        
    ${degreefrom} = 学历要求 
        99:所有（默认）
        01:初中及以下
        02:高中/中技/中专
        03:大专
        04:本科
        05:硕士
        06:博士
        07:无学历要求
    '''
    __base_url = Template(
        "https://search.51job.com/list/${city},${area},0000,00,9,99,${keyword},2,"
        "${page}.html?lang=c&postchannel=0000&workyear=${workyear}&cotype=99&degreefrom=${"
        "degreefrom}&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare=")

    __area_url = "https://js.51jobcdn.com/in/js/2016/layer/area_array_c.js"

    def __init__(self, keyword, workyear="99", degreefrom="99", city="000000", area="000000"):
        self.keyword = keyword
        self.workyear = workyear
        self.degreefrom = degreefrom
        self.city = city
        self.area = area
        self.save_path = "./save/"  # 存储路径
        self.cache_path = "./cache/qcwy_area.txt"  # 缓存路径
        self.row = 2  # 减除标题的两行，记录开始行数
        self.maxRow = 202  # 最大的行数
        self.page = 1  # 当前页数
        self.base_url = self.__base_url.substitute(keyword=self.keyword,
                                                   page=self.page,
                                                   workyear=self.workyear,
                                                   degreefrom=self.degreefrom,
                                                   city=self.city,
                                                   area=self.area)

    # 显示当前关键字
    def show_keyword(self):
        print(self.keyword)

    # 获取区域代码数据 并展示
    def get_area_code(self):
        # 缓存地址
        cache_path = self.cache_path
        # 尝试获取本地缓存
        if os.path.exists(cache_path):
            print("区域数据走缓存")
            # 存在，走本地缓存
            file_cache = open(cache_path, mode="r+", encoding="utf-8")
        else:
            print("区域数据走网络")
            # 不存在，走网络，并缓存
            response = requests.get(__area_url)
            if response.status_code != 200:
                return
            file_cache = open(cache_path, mode="w+", encoding="utf-8")
            file_cache.write(response.text)
            file_cache.seek(0)  # 将光标回到开头，不然等下的read()读不了数据

        file_data = file_cache.read()
        # 获取第一次出现的{ 和最后一次出现的}范围的内容
        pure_data = file_data[file_data.find("{"):file_data.rfind("}") + 1]

        area_data = json.loads(pure_data)

        # 展示数据
        for area in area_data:
            print(area + "=" + area_data[area])

        return area_data

    # 给爷爬
    def do_it(self):
        if not self.keyword:
            print("关键词无效")
            return
        self._init_excel()
        # 循环爬 取数据
        while True:
            self.page += 1
            print(self.base_url)
            response = requests.get(self.base_url, headers=self.__headers)
            if response.status_code != 200:
                # pathlib.Path(__file__).name 获取当前执行的py文件名
                print(pathlib.Path(__file__).name + "请求失败,退出执行")
                return
            # 读取本地文件代替请求，以防请求过多
            # response = open("前程无忧数据.txt", "r", encoding="utf-8").readline()
            base_data = {}
            try:
                base_data = json.loads(response.text)
                # base_data = json.loads(response)
            except TypeError:
                print(pathlib.Path(__file__).name + "数据解析,退出执行")

            job_array = base_data['engine_search_result']
            if len(job_array) == 0 or self.row >= self.maxRow:
                print(pathlib.Path(__file__).name + "没有更多的数据了，结束执行")
                break
            for job in job_array:
                self._write_excel(job, self.row)
                self.row += 1
            print("第%s页" % self.page)
            self.base_url = self.__base_url.substitute(keyword=self.keyword,
                                                       page=self.page,
                                                       workyear=self.workyear,
                                                       degreefrom=self.degreefrom,
                                                       city=self.city,
                                                       area=self.area)
            # 等待一秒循环
            time.sleep(1)

        # 保存表格
        self._save_excel()
        print(pathlib.Path(__file__).name + "执行完毕")

    # 初始化表格
    def _init_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("职位总览")
        self.workbook = workbook
        self.worksheet = worksheet

        # 表头样式
        title_style = xlwt.XFStyle()  # 初始化样式
        font = xlwt.Font()
        # 字体大小，12为字号，20为衡量单位
        font.height = 20 * 12
        # 字体加粗
        font.bold = True
        # 设置单元格对齐方式
        alignment = xlwt.Alignment()
        # 0x01(左端对齐)、0x02(水平方向上居中对齐)、0x03(右端对齐)
        alignment.horz = 0x02
        # 0x00(上端对齐)、 0x01(垂直方向上居中对齐)、0x02(底端对齐)
        alignment.vert = 0x01
        # 设置自动换行
        # alignment.wrap = 1
        # 应用样式
        title_style.font = font
        title_style.alignment = alignment

        # 内容样式
        content_style = xlwt.XFStyle()
        content_font = xlwt.Font()
        # 字体大小，12为字号，20为衡量单位
        content_font.height = 20 * 10
        # 字体加粗
        content_font.bold = False
        # 设置单元格对齐方式
        content_alignment = xlwt.Alignment()
        # 0x01(左端对齐)、0x02(水平方向上居中对齐)、0x03(右端对齐)
        content_alignment.horz = 0x02
        # 0x00(上端对齐)、 0x01(垂直方向上居中对齐)、0x02(底端对齐)
        content_alignment.vert = 0x01
        # 设置自动换行
        # content_alignment.wrap = 1
        content_style.font = content_font
        content_style.alignment = content_alignment

        self.content_style = content_style
        self.title_style = title_style

        # 单元格宽度
        worksheet.col(0).width = 3333
        worksheet.col(1).width = 3333
        worksheet.col(2).width = 3333
        worksheet.col(3).width = 3333
        worksheet.col(4).width = 3333
        worksheet.col(5).width = 3333
        worksheet.col(6).width = 3333
        worksheet.col(7).width = 3333
        worksheet.col(8).width = 3333
        worksheet.col(9).width = 3333
        worksheet.col(10).width = 3333

        # 表头内容
        worksheet.write(0, 0, "关键词", title_style)
        worksheet.write(0, 1, self.keyword, content_style)
        worksheet.write(0, 2, "区域", title_style)
        # worksheet.write(0, 3, "NaN", content_style)
        worksheet.write(0, 4, "数据", title_style)
        # worksheet.write(0, 5, "NaN", content_style)
        worksheet.write(1, 0, "职位", title_style)
        worksheet.write(1, 1, "职位类型", title_style)
        worksheet.write(1, 2, "薪资范围", title_style)
        worksheet.write(1, 3, "工作地点", title_style)
        worksheet.write(1, 4, "工作经验", title_style)
        worksheet.write(1, 5, "学历", title_style)
        worksheet.write(1, 6, "招几人", title_style)
        worksheet.write(1, 7, "公司", title_style)
        worksheet.write(1, 8, "公司类型", title_style)
        worksheet.write(1, 9, "公司规模", title_style)
        worksheet.write(1, 10, "公司福利", title_style)

    # 插入数据 job数据实体 row 行
    def _write_excel(self, job, row):
        if not self.worksheet:
            return
        try:
            self.worksheet.write(row, 0, job.get("job_name", ""), self.content_style)
            self.worksheet.write(row, 1, job.get("companyind_text", ""), self.content_style)
            self.worksheet.write(row, 2, job.get("providesalary_text", ""), self.content_style)
            count = 3
            for attr in job.get("attribute_text"):
                self.worksheet.write(row, count, attr, self.content_style)
                count += 1
            self.worksheet.write(row, 7, job.get("company_name", ""), self.content_style)
            self.worksheet.write(row, 8, job.get("companytype_text", ""), self.content_style)
            self.worksheet.write(row, 9, job.get("companysize_text", ""), self.content_style)
            welfare = ""
            for st in job.get("jobwelf"):
                welfare += st
            self.worksheet.write(row, 10, welfare, self.content_style)
        except Exception as e:
            print("解析出错了一条数据：" + str(e))

    # 存储表格
    def _save_excel(self):
        if not self.workbook:
            return
        self.worksheet.write(0, 3, self.city + "," + self.area, self.content_style)
        self.worksheet.write(0, 5, str(self.row - 2), self.content_style)
        self.workbook.save(self.save_path + "qcwy_" + str(int(round(time.time() * 1000))) + ".xls")
