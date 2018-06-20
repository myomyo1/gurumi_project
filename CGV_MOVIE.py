from pymongo import MongoClient

client = MongoClient('mongodb://192.168.1.56:27017')
db_ttolae = client.TTOLAE
cgv_movie_info = db_ttolae.cgv_movie_info

import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from selenium import webdriver

driver = webdriver.Chrome('../../../Desktop/chromedriver.exe')

base_url = "http://www.cgv.co.kr/movies/"

for i in range(1, 320):
    html = urlopen(base_url + "finder.aspx?s=true&sdate=1960&edate=2020&page=" + str(i))  # 무비파인더 1페이지부터 319페이지까지 돌리기
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find('div', class_='wrap-movie').findAll("a", href=re.compile("^(/movies/detail-view/)"))  # 페이지마다 상세정보페이지로 들어가는 a태그 20개
    link_set = set([urljoin(base_url, a.attrs['href']) for a in link])  # 리스트 컴프리헨션 , 셋으로 만들기 한페이지에 해당되는 a태그 20개기 리스트에서 셋으로
    print(link_set)

    for detail_link in link_set:

        wastelink = "http://www.cgv.co.kr/movies/detail-view/?midx=80625"
        if detail_link == wastelink: continue


        driver.get(detail_link)  # 셀레니움으로 크롬 열고 디테일링크 하나 들어가기
        detail_html = driver.page_source
        detail_soup = BeautifulSoup(detail_html, 'html.parser')

        if detail_soup.find("div", class_="sect-error") == None:
            pass
        else :
            errorcheck = detail_soup.find("div", class_="sect-error").find("h3").get_text()
            if ('이용에' in errorcheck) or ('불편을' in errorcheck) or ('드려' in errorcheck) or ('죄송합니다.' in errorcheck):
                xpath = """//*[@id="contents"]/div/a[1]/span"""
                driver.find_element_by_xpath(xpath).click()
                time.sleep(0.1)
                continue

        movie_id = detail_link.replace("http://www.cgv.co.kr/movies/detail-view/?midx=", "")  # 링크 주소값에서 영화 id만 추출

        if detail_soup.find("div", class_="spec").find('a') == None :
            direc = " "
        else :
            try:
                direc = detail_soup.find("div", class_="spec").find('a').get_text()
                direc= re.search(r'[a-zA-Zㄱ-힣.\s]+', direc).group()
            except AttributeError as e:
                pass

        try:
            movie_title = detail_soup.find("div", class_="sect-base-movie").find('strong').get_text()
            movie_title = movie_title.strip()

        except AttributeError as e:
            pass

        #평점
        egg = detail_soup.find("div", class_="egg-gage small").find(class_="percent").get_text()
        egg = egg.strip()

        if egg == "?":
            egg=0.0
        else:
            egg = float(egg[:-1])/10

        #리뷰 개수
        if detail_soup.find("span",class_="msg-em") == None :
            review_cnt = 0
        elif detail_soup.find("span",class_="msg-em").find(id="cgvEggCountTxt").get_text() != None:
            review_cnt = detail_soup.find("span",class_="msg-em").find(id="cgvEggCountTxt").get_text()
            if len(review_cnt) > 3:
                review_cnt = int(review_cnt.replace(",", ""))
            else:
                review_cnt = int(review_cnt)

        #성별 예매율
        if detail_soup.find("ul", class_="graph") == None:
            male = 0.0
        elif detail_soup.find("ul", class_="graph") != None:
            male = detail_soup.find("span", class_="jqplot-donut-series jqplot-data-label").get_text().strip()
            male = male[2:-1]
            if "." in male:
                male = float(male.replace(".", "")) / 10
            else:
                male = float(male)

        #연령별 예매율
        if detail_soup.find("div", id="jqplot_age") == None:
            teen = 0
            twenty = 0
            thirty = 0
            forty = 0
        elif detail_soup.find("div", id="jqplot_age") != None:
            teen = detail_soup.find("div", class_="jqplot-point-label jqplot-series-0 jqplot-point-0").get_text()
            twenty = detail_soup.find("div", class_="jqplot-point-label jqplot-series-0 jqplot-point-1").get_text()
            thirty = detail_soup.find("div", class_="jqplot-point-label jqplot-series-0 jqplot-point-2").get_text()
            forty = detail_soup.find("div", class_="jqplot-point-label jqplot-series-0 jqplot-point-3").get_text()
            if "." in teen:
                teen = float(teen.replace(".", "")) / 10
            else:
                teen = float(teen)
            if "." in twenty:
                twenty = float(twenty.replace(".", "")) / 10
            else:
                twenty = float(twenty)
            if "." in thirty:
                thirty = float(thirty.replace(".", "")) / 10
            else:
                thirty = float(thirty)
            if "." in forty:
                forty = float(forty.replace(".", "")) / 10
            else:
                forty = float(forty)

        movie = { "_id":movie_id,
                 "movie_id": [{"site":"cgv","id": movie_id}],
                 "movie_title":movie_title,
                 "director":direc,
                 "review_cnt" :[{"site":"cgv","cnt":review_cnt}],
                 "male" : male,
                 "age" : {"teen":teen, "twenty":twenty,"thirty":thirty,"forty":forty},
                 "score":[{"site":"cgv","grade":egg}] }

        print(movie)
        cgv_movie_info.save(movie)








