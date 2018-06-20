# from pymongo import MongoClient
#
# client = MongoClient('mongodb://192.168.1.56:27017')
# db_ttolae = client.TTOLAE
# cgv_review = db_ttolae.cgv_review

#-----------------------------------------------------------------------------------
# 콘솔 글씨색 변경 용도
# 사용법 : http://parkjuwan.dothome.co.kr/wordpress/2017/06/24/text-color-py/

#글씨색 변경 끝맺음 설정
C_END = "\033[0m"
#글씨 굵게
C_BOLD = "\033[1m"
#반전
C_INVERSE = "\033[7m"

#글씨색
C_BLACK = "\033[30m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"

#글씨 배경색
C_BGBLACK = "\033[40m"
C_BGRED = "\033[41m"
C_BGGREEN = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN = "\033[46m"
C_BGWHITE = "\033[47m"
#------------------------------------------------------------------------------------



################## CGV_REIVEW

import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('../../../Desktop/chromedriver.exe')

try :
    ########################################## 리뷰를 얻어 리뷰 리스트에 담는 함수정의 #############################################
    def get_review():

        detail_html = driver.page_source
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        reviews_div = detail_soup.find('div', class_='wrap-persongrade')

        try:
            realid = [userid.find("a").attrs['data-moreuserid'] for userid in reviews_div.findAll("li", {"class": "writer-name"})]
        except AttributeError as e:
            pass

        try:
            reviews = [review.get_text() for review in reviews_div.find("ul", id="movie_point_list_container").findAll("div", class_="box-comment")]  # findAll => 엘리먼트'들'   # 하나씩 돌면서 필요한 텍스트 뽑아내기(get_text())
        except AttributeError as e:
            pass

        try:
            rDate = [reportingDate.get_text() for reportingDate in reviews_div.findAll("span", class_="day")]
        except AttributeError as e:
            pass

        for i in range(0, len(reviews)):
            review = {"movie_id": movie_id, "site": "cgv", "user_id": realid[i], "review_contents": reviews[i], "reg_date": rDate[i]}
            review_list.extend([review])
            # cgv_review.save(review)
            print(review)

    def wait():
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "movie_point_list_container")))
        time.sleep(0.2)

    #############################################################################################################################


    # 크롤링 시작
    base_url = "http://www.cgv.co.kr/movies/"
    for i in range(1, 320):

        # 무비파인더 1페이지부터 319페이지까지 돌리기
        html = urlopen(base_url + "finder.aspx?s=true&sdate=1960&edate=2020&page=" + str(i))
        soup = BeautifulSoup(html, "html.parser")

        # 페이지마다 상세정보페이지로 들어가는 a태그 20개 찾기
        link = soup.find('div', class_='wrap-movie').findAll("a", href=re.compile("^(/movies/detail-view/)"))

        # 리스트 컴프리헨션 , 셋으로 만들기 한페이지에 해당되는 a태그 20개기 리스트에서 셋으로 페이지마다 찾아짐
        link_set = set([urljoin(base_url, a.attrs['href']) for a in link])

        # 영화 URL 리스트
        print( i , "번째 페이지 :" , link_set)

        # 영화 상세 정보 페이지 URL
        for detail_link in link_set:

            # 셀레니움으로 크롬 열고 디테일링크 하나 들어가기
            driver.get(detail_link)
            detail_html = driver.page_source
            detail_soup = BeautifulSoup(detail_html, 'html.parser')

            #이용에 불편을 드려 죄송합니다 페이지 발생시
            if detail_soup.find("div", class_="sect-error") == None:
                pass
            else :
                errorcheck = detail_soup.find("div", class_="sect-error").find("h3").get_text()
                if ('이용에' in errorcheck) or ('불편을' in errorcheck) or ('드려' in errorcheck) or ('죄송합니다.' in errorcheck):
                    xpath = """//*[@id="contents"]/div/a[1]/span"""
                    driver.find_element_by_xpath(xpath).click()
                    wait()
                    continue

            movie_id = detail_link.replace("http://www.cgv.co.kr/movies/detail-view/?midx=", "")  # 링크 주소값에서 영화 id만 추출

            ############################################### XPATH로 페이지이동 ###################################################

            # 영화 한개당 리뷰 리스트 객체 초기화
            review_list = []

            #리뷰 페이지 개수를 얻다가 AttributeError 예외가 발생할 때가 있어서 따로 구성했음
            try:
                review_page_list_count = len(list(detail_soup.find("ul", id="paging_point").children))
            except AttributeError:
                continue

            # 리뷰 개수
            if detail_soup.find("span", class_="msg-em") == None:
                review_cnt = 0
            elif detail_soup.find("span", class_="msg-em").find(id="cgvEggCountTxt").get_text() != None:
                review_cnt = detail_soup.find("span", class_="msg-em").find(id="cgvEggCountTxt").get_text()
                if len(review_cnt) > 3:
                    review_cnt = int(review_cnt.replace(",", ""))
                else:
                    review_cnt = int(review_cnt)

            # 리뷰가 존재하지 않아 페이지가 없을때
            if review_page_list_count == 0:
                review = {"movie_id": movie_id, "site": "cgv", "user_id": " ", "review_contents": " ", "reg_date": " "}
                review_list.extend([review])
                # cgv_review.save(review)
                print(review)


            # 리뷰가 존재하지만 페이지가 10개 이하일때
            elif review_cnt <= 60:

                if review_cnt <= 6:
                    get_review()

                else:
                    lessthanten = int(review_cnt / 6)
                    lessthanten2 = int(review_cnt % 6)

                    if lessthanten2 == 0:
                        for i in range(1, lessthanten + 1):
                            xpath = """//*[@id="paging_point"]/li[""" + format(i) + """]/a"""
                            driver.find_element_by_xpath(xpath).click()
                            wait()
                            get_review()
                    else:
                        for i in range(1, lessthanten + 2):
                            xpath = """//*[@id="paging_point"]/li[""" + format(i) + """]/a"""
                            driver.find_element_by_xpath(xpath).click()
                            wait()
                            get_review()


            # 리뷰 페이지 개수가 10개 이상일때
            else:
                xpath = """//*[@id="paging_point"]/li[12]/button"""  # 끝페이지로 이동해서
                driver.find_element_by_xpath(xpath).click()
                wait()
                get_review()

                # 이전버튼 클릭 이동 관련 정보 획득
                detail_html = driver.page_source
                detail_soup = BeautifulSoup(detail_html, 'html.parser')

                lastPageNo = detail_soup.find("div", class_="paging").find("li", class_="on").get_text()  # 마지막페이지 번호
                lastPageNo = int(lastPageNo)

                if lastPageNo % 10 == 0:
                    countPrev = int(lastPageNo / 10) - 1  # 이전버튼 몇번 누를지
                    repeat = 9  # 마지막 페이징그룹에 몇개 페이지가 있는가
                    lastXpathValue = (lastPageNo % 10) + 12  # 마지막페이지 xpath값

                else:
                    countPrev = int(lastPageNo / 10)  # 이전버튼 몇번 누를지
                    repeat = (lastPageNo % 10 - 1)  # 마지막 페이징그룹에 몇개 페이지가 있는가
                    lastXpathValue = (lastPageNo % 10) + 2  # 마지막페이지 xpath값

                # print("이전버튼 누르는 횟수", countPrev)
                # print("마지막페이징그룹에 페이지 개수", repeat)
                # print("마지막페이지 xpath값", lastXpathValue)

                xpathIndex = lastXpathValue - 1  # 인덱스초기화

                # 마지막 페이징 그룹
                for i in range(0, repeat):
                    xpath = """//*[@id="paging_point"]/li[""" + str(xpathIndex - i) + """]/a"""
                    driver.find_element_by_xpath(xpath).click()
                    wait()
                    get_review()

                    # 이전버튼 페이징 그룹
                for j in range(0, countPrev):
                    xpath = """//*[@id="paging_point"]/li[2]/button"""
                    driver.find_element_by_xpath(xpath).click()
                    wait()
                    get_review()

                    if j == countPrev - 1:
                        for i in range(0, 9):
                            xpath = """//*[@id="paging_point"]/li[""" + str(9 - i) + """]/a"""
                            driver.find_element_by_xpath(xpath).click()
                            wait()
                            get_review()

                    else:
                        for i in range(0, 9):
                            xpath = """//*[@id="paging_point"]/li[""" + str(11 - i) + """]/a"""
                            driver.find_element_by_xpath(xpath).click()
                            wait()
                            get_review()


            # 요위치에서 DB 에 저장하면 리스트 단위로 저장 할 수 있음..
            # 개별 단위 저장 하려면 get_review() 함수 내부에서 하면됨
            # print(C_BOLD + C_BLUE, "현재 영화 제목 : " + movie_name + "  /// 리뷰 개수 : ", len(review_list), C_END)
            # for index, r in enumerate(review_list):
            #     print("리뷰 no.",index+1,r)
            #
            # # 한줄 띄우기용도
            # print()
finally:
    driver.quit()