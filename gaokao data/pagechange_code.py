# coding=UTF-8
from bs4 import BeautifulSoup as bs   # 解析网页，获取数据
import re  # 正则表达式
from selenium import webdriver  # 获取网页信息
from selenium.webdriver.chrome.options import Options
import time
import random
import xlwt
import os
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
#创建excel
excelfile = xlwt.Workbook(encoding="utf-8", style_compression=0)
excelsheet = excelfile.add_sheet('sheet1', cell_overwrite_ok=True)
col = ("年份" ,"学校名称", "考生所在地", "所选大类", "录取批次","最低分/最低位次", "招生类型","报考要求")#2021 北京大学，北京，物理类/历史类/综合，本科一批，700/200，普通类，不限/无
for i in range(8):
    excelsheet.write(0, i, col[i])
print("excel创建成功")
#创建正则表达式
university_name=re.compile(r'<span class="line1-schoolName" style="color: white;">(.*)</span>')  # 学校名称
stu_pl=re.compile(r'">([\u4E00-\u9FFF]*)</div>')  # 考生所在省份
scores=re.compile(r'<td>(\d{3}[/](\d{1,})?[-]?)</td>')   # 高考成绩
other=re.compile(r'>(([\u4E00-\u9FFF]*?)[A-Z]?[/]?[，]?([\u4E00-\u9FFF]*?)([(][0-9][\u4E00-\u9FFF][0-9][)])?)</td>')  # 其他信息
subject_type=re.compile(r'<div class="ant-select-selection-selected-value" style="display: block; opacity: 1;" title="([\u4E00-\u9FFF]*)">')  # 选科大类
def main():
    line_num = 1
    error_list=[]
    baseurl = 'https://www.gaokao.cn/school/'
    # 1.爬取网页
    for i in range(30, 2000):
        try:
            url=baseurl+str(i)
            un_name,info_63,info_12,info_old=askurl(url)
            name,total=pardata(un_name,info_63,info_12,info_old)
            x=save_excel(name,total,line_num)
            line_num=x
            excelfile.save("gaokao scores.xlsx")
        except :
            print("error",i)
            error_list.append(i)
            pass
    text_create('error_list',error_list)

def text_create(name, msg):
    desktop_path = r'E:\pycharm\pythonProject\venv'
    full_path = desktop_path + name + '.txt'  # 也可以创建一个.doc的word文档
    file = open(full_path, 'w')
    file.write(msg)
    file.close()




def askurl(url):
    info_63=[] #6选3省份
    info_12=[] #3+2+1省份
    info_old=[] #老高考省份
    chrome_options = Options()
    driver = webdriver.Chrome(executable_path=r'E:\Program Files\chromedriver.exe', options=chrome_options)
    driver.get(url)
    driver.maximize_window()
    time.sleep(random.randint(3,10))
    driver.find_element_by_xpath('//ul//span[text()="历年分数"]').click()
    time.sleep(random.randint(5,15))
    maininformation=driver.page_source
    info_63.append(maininformation)
    pages='//*[@class="ant-select-dropdown-menu-item"]'
    for i in range(1,30): #跳过新疆，吉林
        if i==6 or i==8:
            continue
        page=pages+str([i])
        driver.find_element_by_xpath('//*[@id="proline"]/div[1]/div/div[1]/div/div/span').click()
        time.sleep(random.randint(5,10))
        driver.find_element_by_xpath(page).click()
        time.sleep(random.randint(3,10))
        html_1=driver.page_source
        if  i==1 or i==10 or i==14 or i==20:
            info_63.append(html_1)
        else:
            html_all=[]
            html_all.append(html_1)
            textname='//ul//li[text()='
            if i==2 or i==5 or i==9 or i==12 or i==16 or i==17 or i==18 or i==21:
                textname=textname+'"历史类"]'
                driver.find_element_by_xpath('//*[@id="proline"]/div[1]/div/div[3]/div/div/span').click()
                time.sleep(random.randint(3,10))
                driver.find_element_by_xpath(textname).click()
                time.sleep(random.randint(3,10))
                html_2 = driver.page_source
                html_all.append(html_2)
                info_12.append(html_all)
            else:
                textname=textname+'"文科"]'
                driver.find_element_by_xpath('//*[@id="proline"]/div[1]/div/div[3]/div/div/span').click()
                time.sleep(random.randint(3,10))
                driver.find_element_by_xpath(textname).click()
                time.sleep(random.randint(3,10))
                html_2=driver.page_source
                html_all.append(html_2)
                info_old.append(html_all)
        time.sleep(random.randint(3,10))
    return maininformation,info_63,info_12,info_old
#解析并存储数据
def pardata(un_name,info_63,info_12,info_old):
    # 数据归类
    totals=[]
    #1。学校名处理
    name=un_name_process(un_name)
    # 新高考省份
    # 1.六选三
    for i in range(len(info_63)):
        student_province, other_info, score=basic_info_process(info_63[i])
        if i==1 or i==2 or i==3 :
            all_info=data_process_2(other_info, score)
        else:
            all_info=data_process_1(other_info, score,i)
        all_info.append(student_province)
        totals.append(all_info)
    #2. 3+2+1(物理类，历史类)
    for i in range(len(info_12)):
        if i ==0 or i==1 or i==7 :
            for r in info_12[i]:
                student_province, other_info, score = basic_info_process(r)
                su_type=subject(r)
                all_info=data_process_2(other_info, score)
                all_info.append(student_province)
                all_info.append(su_type)
                totals.append(all_info)
        else:
            for r in info_12[i]:
                student_province, other_info, score = basic_info_process(r)
                su_type=subject(r)
                all_info=data_process_1(other_info, score,i)
                all_info.append(student_province)
                all_info.append(su_type)
                totals.append(all_info)
    #3.老高考(文理科)
    for i in range(len(info_old)):
        for r in info_old[i]:
            student_province, other_info, score = basic_info_process(r)
            su_type = subject(r)
            all_info = data_process_2(other_info, score)
            all_info.append(student_province)
            all_info.append(su_type)
            totals.append(all_info)
    return name,totals

#保存到excel
def un_name_process(un_name): # 学校名处理
    soup_1 = bs(un_name, 'html.parser')
    for item in soup_1.find_all('div',class_="schoolName clearfix school_view_top"):
        for items in item.find_all('div',class_='line1'):
            items = str(items)
            name = re.findall(university_name, items)[0]
            return name
def basic_info_process(page): #基本信息处理
    soup = bs(page, 'html.parser')
    # 考生所在省份
    for item in soup.find_all('div', id="proline"):
        for items in item.find_all('div', class_="scoreLine-dropDown"):
            items = str(items)
            student_province = re.findall(stu_pl, items)[0]
    for item in soup.find_all('div', class_="schoolLine clearfix", id="proline"):
        for items in item.find_all('tbody'):
            items = str(items)
            other_info = re.findall(other, items)  # 其他信息
            score = re.findall(scores, items)  # 分数
    return student_province,other_info,score
def data_process_1(other,score,i):
    all_info=[]
    try:
        for i in range(1,len(score)+1):
            b=[]
            t=score[i-1]
            b.append(t[0])
            x=other[i*3-3]
            b.append(x[0])
            y=other[i*3-2]
            b.append(y[0])
            z=other[i*3-1]
            b.append(z[0])
            all_info.append(b)
        return all_info
    except Exception:
        print(other,i)
        a=["error"]
        return a
def data_process_2(other,score):
    all_info=[]
    for i in range(1,len(score)+1):
        b=[]
        t=score[i-1]
        b.append(t[0])
        x=other[i*2-2]
        b.append(x[0])
        y=other[i*2-1]
        b.append(y[0])
        all_info.append(b)
    return all_info
def subject(page):
    soup = bs(page, 'html.parser')
    for item in soup.find_all('div',id="proline"):
        for items in item.find_all('div',class_="ant-select-selection__rendered"):
            items=str(items)
            su_type=re.findall(subject_type,items)[0]
    return su_type
#保存至excel
def save_excel(name,total,line):
    for i in range(0,5):
        for r in range(len(total[i])-1):
            excelsheet.write(line, 0, "2021")
            excelsheet.write(line, 1, name)
            excelsheet.write(line, 2, total[i][len(total[i]) - 1])
            excelsheet.write(line, 3, "综合")
            text=total[i][r]
            excelsheet.write(line,4,text[1])
            excelsheet.write(line,5,text[0])
            excelsheet.write(line,6,text[2])
            if i == 0 or i == 4:
                excelsheet.write(line,7,text[3])
            else:
                excelsheet.write(line,7,"null")
            line=line+1

    for i in range(5,21):
        for r in range(len(total[i])-2):
            excelsheet.write(line, 0, "2021")
            excelsheet.write(line, 1, name)
            excelsheet.write(line, 2, total[i][len(total[i]) - 2])
            excelsheet.write(line, 3, total[i][len(total[i]) - 1])
            text=total[i][r]
            excelsheet.write(line,4,text[1])
            excelsheet.write(line,5,text[0])
            excelsheet.write(line,6,text[2])
            if i == 5 or i == 6 or i == 7 or i == 8 or i == 19 or i == 20:
                excelsheet.write(line, 7, "null")
            else:
                excelsheet.write(line, 7, text[3])
            line=line+1
    for i in range(21,len(total)):
        for r in range(len(total[i]) - 2):
            excelsheet.write(line, 0, "2021")
            excelsheet.write(line, 1, name)
            excelsheet.write(line, 2, total[i][len(total[i]) - 2])
            excelsheet.write(line, 3, total[i][len(total[i]) - 1])
            text = total[i][r]
            excelsheet.write(line, 4, text[1])
            excelsheet.write(line, 5, text[0])
            excelsheet.write(line, 6, text[2])
            excelsheet.write(line, 7, "null")
        line=line+1
    print(name,"数据保存完毕")
    return line
if __name__ == '__main__':
    main()


#北京序号为0
#爬取学校对应不同省份数据需要分新高考模式和老高考模式
#新高考省份：北京1 天津2 山东15 上海9 海南20
#“3+1+2”方案的湖南18、河北3、辽宁6、江苏10、福建13、湖北17、广东19、重庆21
#1，2，3，6，9，10，13，15，17，18，19，21
#不需要页面切换 1，2，11，15 21