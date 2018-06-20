from pymongo import MongoClient

client = MongoClient('mongodb://192.168.1.56:27017')
db_ttolae = client.TTOLAE
naver_review = db_ttolae.naver_review

import time
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('C:/Users/BIT/Desktop/chromedriver.exe')

driver.get('https://www.naver.com')

elem_login = driver.find_element_by_id("id")
elem_login.clear()
elem_login.send_keys('')  # 네이버 아이디

elem_login = driver.find_element_by_id("pw")
elem_login.clear()
elem_login.send_keys('')  # 네이버 패스워드

loginxpath = """//*[@id="frmNIDLogin"]/fieldset/span/input"""
driver.find_element_by_xpath(loginxpath).click()

n = 20001


# xpath 나올때까지 기다리는 함수 정의
def wait_xpath(XPATH):
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, XPATH)))
    time.sleep(0.6)


# title 로 현재 읽어진 페이지가 오류 페이지인지 확인 함수정의
def wait_title_check(soup):
    # title 태그를 읽어오기 전에 오류체크를 해서 밑에 if 문이 제대로 예외로 처리가 안되고 멈추는거같음 그래서 추가함
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
    # html 오류
    errorcheck = soup.find('title').get_text()
    return errorcheck


def wait_review():
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "score_result")))
    time.sleep(0.6)


while n <= 174747:
    try:
        time.sleep(0.1)
        driver.get('https://movie.naver.com/movie/bi/mi/basic.nhn?code=' + str(n))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

    except UnexpectedAlertPresentException as e:
        Alert(driver).accept()
        n = n + 1
        continue

    except AttributeError as e:
        n = n + 1
        continue

    except Exception as ex:
        continue

    # 서버 막혔을때 15분 타임슬립
    if (len(soup.get_text())) == 0:
        time.sleep(900)
        continue

    # html 오류
    errorcheck = wait_title_check(soup)
    if ('Server Error' in errorcheck) or ('HTTP Status' in errorcheck) or ('502' in errorcheck) or ('오류입니다' in errorcheck):
        continue

    if soup.find("dl", class_="info_spec").find("dt", class_="step2") == None or soup.find("dl", class_="info_spec").find("dt", class_="step3") == None:  # 감독, 배우진 없는 영화 패스
        pass
    else:  # 감독, 배우진 있는 영화만 읽기

        movie_div = soup.find("div", class_='mv_info_area')

        # 영화 아이디 -> 시퀀스
        movie_id = n

        driver.get("https://movie.naver.com/movie/bi/mi/point.nhn?code=" + str(movie_id))

        driver.switch_to.frame("pointAfterListIframe")  # Iframe loading

        pointhtml = driver.page_source
        pointsoup = BeautifulSoup(pointhtml, "html.parser")

        errorcheck2 = wait_title_check(pointsoup)
        if ('Server Error' in errorcheck2)  or ('HTTP Status' in errorcheck2) or ('502' in errorcheck2) or ('오류입니다' in errorcheck2):
            continue

        review_div = pointsoup.find("div", class_="score_result")

        review_cnt_list = pointsoup.find("strong", class_="total").findAll("em")
        review_cnt = review_cnt_list[1].get_text()
        review_cnt = int(review_cnt.replace(",", ""))

        # 리뷰없을때
        if review_cnt == 0:
            review = {"movie_id": movie_id, "site": "naver", "user_id": " ", "user_grade": " ", "review_contents": " ", "reg_date": " "}
            naver_review.save(review)
            print(review)

        # 리뷰 10개 미만
        elif 0 < review_cnt <= 10:

            grade_list = [grade.find('em') for grade in review_div.findAll("div", class_="star_score")]

            for i in range(0, len(grade_list)):
                if grade_list[i] == None:
                    grade_list[i] = 5
                else:
                    grade_list[i] = grade_list[i].get_text()

            review_list = [review.find("p").get_text() for review in review_div.findAll("div", class_="score_reple")]

            id_list = review_div.findAll("div", class_="score_reple")
            final_id_list = []
            for id in id_list:
                idlist = id.findAll('span')
                if idlist[0].get_text() == "관람객":
                    final_id_list.append(idlist[1].get_text())
                else:
                    final_id_list.append(idlist[0].get_text())

            review_date = [review_date.findAll("em")[1].get_text() for review_date in review_div.findAll("dt")]
            for i in range(0, review_cnt):
                review_date[i] = review_date[i][:10]

            for i in range(0, review_cnt):
                review = {"movie_id": movie_id, "site": "naver", "user_id": final_id_list[i], "user_grade": grade_list[i], "review_contents": review_list[i], "reg_date": review_date[i]}
                naver_review.save(review)
                print(review)

        # 리뷰 10개 이상
        elif 10 < review_cnt:

            click_cnt = int(review_cnt / 10)
            # print("클릭몇번해야하는지 : ", click_cnt)

            final_page_review_cnt = review_cnt % 10

            if final_page_review_cnt == 0:
                click_cnt = click_cnt - 1
                final_page_review_cnt = 10

            grade_list = [grade.find('em') for grade in review_div.findAll("div", class_="star_score")]

            for i in range(0, len(grade_list)):
                if grade_list[i] == None:
                    grade_list[i] = 5
                else:
                    grade_list[i] = grade_list[i].get_text()

            review_list = [review.find("p").get_text() for review in review_div.findAll("div", class_="score_reple")]

            id_list = review_div.findAll("div", class_="score_reple")
            final_id_list = []
            for id in id_list:
                idlist = id.findAll('span')
                if idlist[0].get_text() == "관람객":
                    final_id_list.append(idlist[1].get_text())
                else:
                    final_id_list.append(idlist[0].get_text())

            review_date = [review_date.findAll("em")[1].get_text() for review_date in review_div.findAll("dt")]
            for i in range(0, 10):
                review_date[i] = review_date[i][:10]

            for i in range(0, 10):
                review = {"movie_id": movie_id, "site": "naver", "user_id": final_id_list[i], "user_grade": grade_list[i], "review_contents": review_list[i], "reg_date": review_date[i]}
                naver_review.save(review)
                print(review)

            # 리뷰페이지 이동
            for i in range(2, click_cnt + 2):
                if i == click_cnt + 1:  # 마지막 페이지 일때

                    try :
                        xpath = """//*[@id="pagerTagAnchor""" + str(i) + """"]/em"""
                        wait_xpath(xpath)
                        driver.find_element_by_xpath(xpath).click()
                    except (NoSuchElementException, TimeoutException ) as e :
                        print("xpath 존재 안함 예외내용 : " , e)
                        # driver.execute_script("window.history.go(-1)")  #뒤로가기
                        xpath = """//*[@id="pagerTagAnchor""" + str(i - 3) + """"]/span"""
                        wait_xpath(xpath)
                        driver.find_element_by_xpath(xpath).click()

                        xpath = """//*[@id="pagerTagAnchor""" + str(i - 1) + """"]/span"""
                        wait_xpath(xpath)
                        driver.find_element_by_xpath(xpath).click()

                    pointhtml = driver.page_source
                    pointsoup = BeautifulSoup(pointhtml, "html.parser")

                    try:
                        wait_review()
                        ##추가된부분

                    except Exception as e :
                        print("score_result 존재 안함 예외내용 : ", e)
                        driver.execute_script("window.history.go(-1)")  # 뒤로가기
                        continue

                    if pointsoup.find("div", class_="score_result") == None:
                        continue
                    else : review_div =  pointsoup.find("div", class_="score_result")
                    ##

                    grade_list = [grade.find('em') for grade in review_div.findAll("div", class_="star_score")]

                    for i in range(0, len(grade_list)):
                        if grade_list[i] == None:
                            grade_list[i] = 5
                        else:
                            grade_list[i] = grade_list[i].get_text()

                    review_list = [review.find("p").get_text() for review in review_div.findAll("div", class_="score_reple")]

                    id_list = review_div.findAll("div", class_="score_reple")
                    final_id_list = []
                    for id in id_list:
                        idlist = id.findAll('span')
                        if idlist[0].get_text() == "관람객":
                            final_id_list.append(idlist[1].get_text())
                        else:
                            final_id_list.append(idlist[0].get_text())

                    review_date = [review_date.findAll("em")[1].get_text() for review_date in review_div.findAll("dt")]
                    for i in range(0, final_page_review_cnt):
                        review_date[i] = review_date[i][:10]

                    for i in range(0, final_page_review_cnt):
                        review = {"movie_id": movie_id, "site": "naver", "user_id": final_id_list[i], "user_grade": grade_list[i], "review_contents": review_list[i], "reg_date": review_date[i]}
                        naver_review.save(review)
                        print(review)

                else:  # 마지막 페이지가 아닐때

                    try :
                        xpath = """//*[@id="pagerTagAnchor""" + str(i) + """"]/em"""
                        wait_xpath(xpath)
                        print("예외처리 전 " , i)
                        driver.find_element_by_xpath(xpath).click()
                    except (NoSuchElementException, TimeoutException) as e:
                        print("xpath 존재 안함 예외내용 : ", e)
                        # driver.execute_script("window.history.go(-1)")  #뒤로가기
                        xpath = """//*[@id="pagerTagAnchor""" + str(i - 3) + """"]/span"""
                        wait_xpath(xpath)
                        time.sleep(0.6)
                        driver.find_element_by_xpath(xpath).click()

                        xpath = """//*[@id="pagerTagAnchor""" + str(i - 1) + """"]/span"""
                        wait_xpath(xpath)
                        driver.find_element_by_xpath(xpath).click()

                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                        print("aaaaaa" , i)
                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

                        wait_xpath(xpath)
                        time.sleep(0.6)
                        driver.find_element_by_xpath(xpath).click()

                    pointhtml = driver.page_source
                    pointsoup = BeautifulSoup(pointhtml, "html.parser")

                    try:
                        ##추가된부분
                        wait_review()
                    except Exception as e :
                        print("score_result 존재 안함 예외내용 : ", e)
                        driver.execute_script("window.history.go(-1)")  # 뒤로가기
                        continue

                    if pointsoup.find("div", class_="score_result") == None:
                        continue
                    else : review_div =  pointsoup.find("div", class_="score_result")
                    ##

                    grade_list = [grade.find('em') for grade in review_div.findAll("div", class_="star_score")]

                    for i in range(0, len(grade_list)):
                        if grade_list[i] == None:
                            grade_list[i] = 5
                        else:
                            grade_list[i] = grade_list[i].get_text()

                    review_list = [review.find("p").get_text() for review in review_div.findAll("div", class_="score_reple")]

                    id_list = review_div.findAll("div", class_="score_reple")
                    final_id_list = []
                    for id in id_list:
                        idlist = id.findAll('span')
                        if idlist[0].get_text() == "관람객":
                            final_id_list.append(idlist[1].get_text())
                        else:
                            final_id_list.append(idlist[0].get_text())

                    review_date = [review_date.findAll("em")[1].get_text() for review_date in review_div.findAll("dt")]
                    for i in range(0, 10):
                        review_date[i] = review_date[i][:10]

                    for i in range(0, 10):
                        review = {"movie_id": movie_id, "site": "naver", "user_id": final_id_list[i], "user_grade": grade_list[i], "review_contents": review_list[i], "reg_date": review_date[i]}
                        naver_review.save(review)
                        print(review)
    n = n + 1