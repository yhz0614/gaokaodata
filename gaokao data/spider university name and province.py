# coding=UTF-8
from bs4 import BeautifulSoup as bs   # 解析网页，获取数据
import re  # 正则表达式
from selenium import webdriver  # 获取网页信息
from selenium.webdriver.chrome.options import Options
import xlwt  # 存入excel
import time
import random
import os
#创建一个txt文件
desktop_path=r'E:\pycharm\pythonProject\gaokao data'
full_path= desktop_path +r'\universityName_error_list.txt'
file=open(full_path,'w')
file.write('error_list:')
file.close()
# 创建正则表达式对象
major=re.compile(r'<td>(.*)<td>')  #  专业类别
majors=re.compile(r'<p class="cursor major_item_name hover_style" style="float: left;">(([\u4E00-\u9FFF]*)[（]?([\u4E00-\u9FFF]*?)[（]?([\u4E00-\u9FFF]*?)[）]?([\u4E00-\u9FFF]*?)[）]?)</p><i aria-label="icon: play-circle" class="anticon anticon-play-circle"',re.S) # 专业名称
university=re.compile(r'<span class="line1-schoolName" style="color: white;">(.*)</span>') # 学校名称
place=re.compile('<i></i>(.*)</span>') # 学校地址
# 创建excel
excelfile = xlwt.Workbook(encoding="utf-8", style_compression=0)
excelsheet = excelfile.add_sheet('sheet1', cell_overwrite_ok=True)
col = ("学校名称", "学校地址", "学校专业类别", "专业名称")
for i in range(4):
    excelsheet.write(0, i, col[i])
print("excel创建成功")
def main():
    line_num=1
    baseurl = 'https://www.gaokao.cn/school/'
    # 1.爬取网页
    for i in range(2547, 4000):
        try:
            url=baseurl+str(i)
            datas=askurl(url)
            print(i)
        #2.获取并解析数据
            university_data,ma_major,lt_major=parerdata(i,datas)
            time.sleep(random.randint(3,10))
            a=savedata(university_data,ma_major,lt_major,line_num)
            line_num=a
            excelfile.save("universitydata.xls")
            if i%100==0:
                print("100所学校数据保存成功")
        except:
            print("error"+'i')
            text_add(str(i))
            pass

#打开网页爬取数据
def askurl(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=r'E:\Program Files\chromedriver.exe', options=chrome_options)
    driver.get(url)
    time.sleep(random.randint(3,15))
    driver.find_element_by_xpath('//ul//span[text()="开设专业"]').click()
    time.sleep(random.randint(5,15))
    gradepage = driver.page_source
    return gradepage
#解析并保存数据
def parerdata(x,data):
    # 获取当前学校名称和地址
    un_data = []  # 存储一所大学信息
    soup = bs(data, 'html.parser')  # 查找符合要求的字符串，提取内容
    for item in soup.find_all('div',class_="schoolName clearfix school_view_top"):
        for item_1 in item.find_all('div', class_="line1"):
            item_1 = str(item_1)
            name = re.findall(university, item_1)[0]
            un_data.append(name)
        for item_2 in item.find_all('span', class_="line1-province"):
            item_2 = str(item_2)
            city = re.findall(place, item_2)[0]
            un_data.append(city)
    # 获取当前学校所含专业
    main_major = []  # 存放主要专业类别
    lt_major = []  # 存放专业名称
    for item in soup.find_all('div', class_="professional_content"):
        for item_1 in item.find_all('tr'):
            item_1 = str(item_1)
            bmajor = re.findall(major, item_1)
            main_major.append(bmajor)
    for item in soup.find_all('div', class_="professional_content"):
        for item_3 in item.find_all('tr'):
            item_3=str(item_3)
            smajor=re.findall(majors,item_3)
            lt_major.append(smajor)
    for i in range(0,len(main_major)):
        main_major[i]=str(main_major[i]).replace("</td>",'')
    #前面两组元素为国家特色专业，有的学校有，有的学校没有，应视情况而定
    if main_major[0] == "['国家特色专业']" :
        del main_major[0: 2]
        del lt_major[0:2]
    else:
        del main_major[0]
        del lt_major[0]
    # 将列表转化为字符串
    for i in range(0,len(main_major)):
        main_major[i] = str(main_major[i]).replace('[', '')
        main_major[i] = str(main_major[i]).replace(']', '')
    #提取专业名称
    major_name = []
    for r in lt_major:
        t=[]
        for i in range(0,len(r)):
            a=r[i]
            rename=a[0]+' '
            t.append(rename)
        major_name.append(t)
    return un_data,main_major,major_name

#保存到excel
def savedata(un_data,main_major,major_name,line_num):
    #打开excel
    for i in range(0,len(main_major)):
        excelsheet.write(line_num,0,un_data[0])
        excelsheet.write(line_num,1,un_data[1])
        excelsheet.write(line_num,2,main_major[i])
        excelsheet.write(line_num,3,major_name[i])
        line_num=line_num+1
    return line_num
def text_add(msg):
    #打开文档 a+以读写模式打开
    files = open(full_path, 'a+')
    files.write(msg)
    files.write('\n')
    files.close()
if __name__ == '__main__':
    main()