from pymongo import MongoClient
client = MongoClient('mongodb://192.168.1.56:27017')
db_ttolae = client.TTOLAE
naver_movie_info = db_ttolae.naver_movie_info

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('../../../Desktop/chromedriver.exe')

driver.get('http://naver.com')
elem_login = driver.find_element_by_id("id")
elem_login.clear()
elem_login.send_keys('') #네이버 아이디

elem_login = driver.find_element_by_id("pw")
elem_login.clear()
elem_login.send_keys('') #네이버 패스워드

loginxpath = """//*[@id="frmNIDLogin"]/fieldset/span/input"""
driver.find_element_by_xpath(loginxpath).click()

n = 20001

# xpath 기다리는 함수 정의
def wait_xpath(XPATH):
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,XPATH )))

# title 로 현재 읽어진 페이지가 오류 페이지인지 확인 함수정의
def wait_title_check(soup):
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
    # html 오류
    errorcheck = soup.find('title').get_text()
    return errorcheck

#마지막 시퀀스
while n <=174747 :
    try:
        time.sleep(0.1)
        driver.get('https://movie.naver.com/movie/bi/mi/basic.nhn?code='+str(n))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

    except UnexpectedAlertPresentException as e:
        Alert(driver).accept()
        n = n+1
        continue

    except AttributeError as e :
        n = n+1
        continue

    except Exception as ex:
        continue

    #서버 막혔을때 15분 타임슬립
    if (len(soup.get_text())) == 0:
        time.sleep(900)
        continue

    errorcheck = wait_title_check(soup)
    if ('Server Error' in errorcheck) or ('HTTP Status' in errorcheck) or ('502' in errorcheck) or ('오류입니다' in errorcheck) or ('503' in errorcheck):
        print(errorcheck)
        continue

    if soup.find("dl", class_="info_spec").find("dt", class_="step2") == None or soup.find("dl", class_="info_spec").find("dt", class_="step3") == None:  # 감독, 배우진 없는 영화 패스
        pass
    else:  # 감독, 배우진 있는 영화만 읽기

        movie_div = soup.find("div", class_='mv_info_area')

        # 영화 포스터 url
        poster = movie_div.find("div", class_="poster").find('img').attrs['src']

        # 영화 아이디 -> 시퀀스
        movie_id = n

        # 영화제목
        movie_title = movie_div.find('a').get_text()
        if movie_title == "19세 관람가":
            movie_title = movie_div.findAll('a')[1].get_text()

        # 리뷰개수
        try:
            em = soup.find(class_="total").findAll('em')  # soup 에서 em태그 찾기
            review_cnt = int(em[1].get_text().strip().replace(",", ""))  # 해당 em태그에서 텍스트만 읽어서 정리,타입변환

        except AttributeError as e:
            review_cnt = "0"

        naver_review_list = []
        review_dict = {"site":"naver","cnt":review_cnt}
        naver_review_list.append(review_dict)


        # 평점
        try:
            grade = soup.find("div", class_="netizen_score").find("div", class_="star_score").find('em').get_text()
            grade = float(grade.replace(".", "")) / 100  # 정리, 타입변환

        except AttributeError as e:
            grade = "0.00"

        # 평점 탭으로 이동해서 성별, 연령별 예매율 구하기
        length = int((int(len(list(soup.find("ul", id="movieEndTabMenu").children))) - 1) / 2)
        if length < 8:
            xpath = """//*[@id="movieEndTabMenu"]/li[""" + str(length - 2) + """]/a"""
            wait_xpath(xpath)

        else:
            xpath = """//*[@id="movieEndTabMenu"]/li[""" + str(length - 3) + """]/a"""
            wait_xpath(xpath)

        driver.find_element_by_xpath(xpath).click()

        try :
            detail_html = driver.page_source
            detail_soup = BeautifulSoup(detail_html, 'html.parser')
        except Exception as e:
            print(e,"driver 가 페이지를 여는 도중 예외 발생 페이지 다시 열기 시도")
            continue

        # 온클릭으로 새로운 페이지가 열린것이기 때문에 계속 검사해야함
        errorcheck = wait_title_check(detail_soup)
        if ('Server Error' in errorcheck) or ('HTTP Status' in errorcheck) or ('502' in errorcheck) or ('죄송합니다' in errorcheck) or ('오류입니다' in errorcheck) or ('503' in errorcheck):
            print(errorcheck)
            continue

        genderAge = detail_soup.find("div", class_="graph_area")

        if genderAge == None:
            male = 0
            agedictlist = [{'site': 'naver', 'teen': 0, 'twenty': 0, 'thirty': 0, 'forty': 0}]

        else:
            xpath = """//*[@id="netizen_group"]"""
            wait_xpath(xpath)

            driver.find_element_by_xpath(xpath).click()
            try:
                detail_html2 = driver.page_source
                detail_soup2 = BeautifulSoup(detail_html2, 'html.parser')
            except Exception as e:
                print(e, "driver 가 페이지를 여는 도중 예외 발생 페이지 다시 열기 시도")
                continue

            # 온클릭으로 새로운 페이지가 열린것이기 때문에 계속 검사해야함
            errorcheck = wait_title_check(detail_soup2)
            if ('Server Error' in errorcheck) or ('HTTP Status' in errorcheck) or ('502' in errorcheck) or ('죄송합니다' in errorcheck) or ('오류입니다' in errorcheck) or ('503' in errorcheck):
                print(errorcheck)
                continue

            gender_soup = detail_soup2.find("div", id="netizenGenderPointGraph")
            age_soup = detail_soup2.find("div", id="netizenAgePointGraph")

            if gender_soup.find("tspan", style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);") == None:
                male = 0
            else:
                initmale = gender_soup.find("tspan",
                                            style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);").get_text()
                male = int(initmale[:-1])

            # 연령별 점수
            ageratelist = [agerate.find("em").get_text() for agerate in
                           detail_soup2.findAll("span", class_="grp_score3")]

            # 연령별 참여 퍼센트
            agebookingratelist = [initage.get_text() for initage in
                                  age_soup.findAll("tspan", style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);")]

            # 무비 도큐먼트에 붙일 애
            agedictlist = []

            agedict = {'site': 'naver'}
            ageList = ["teen", "twenty", "thirty", "forty"]

            i = 0;
            for index, agerate in enumerate(ageratelist[0:4]):
                if agerate != '0.00':
                    agedict.update({ageList[index]: int(agebookingratelist[i][:-1])})
                    i += 1
                else:
                    agedict.update({ageList[index]: 0})
            agedictlist.append(agedict)


        # 배우, 제작진 탭으로 이동
        xpath = """//*[@id="movieEndTabMenu"]/li[2]/a"""
        wait_xpath(xpath)

        driver.find_element_by_xpath(xpath).click()

        try:
            detail_html = driver.page_source
            detail_soup = BeautifulSoup(detail_html, 'html.parser')
        except Exception as e:
            print(e,"driver 가 페이지를 여는 도중 예외 발생 페이지 다시 열기 시도")
            continue


        # 온클릭으로 새로운 페이지가 열린것이기 때문에 계속 검사해야함
        errorcheck = wait_title_check(detail_soup)
        if ('Server Error' in errorcheck) or ('HTTP Status' in errorcheck) or ('502' in errorcheck) or ('죄송합니다' in errorcheck) or ('오류입니다' in errorcheck) or ('503' in errorcheck):
            print(errorcheck)
            continue

        # 감독
        if detail_soup.find("div", class_="dir_product").find("a") == None:
            direc_id = " "
            direc_name = detail_soup.find("div", class_="dir_product").find("span").attrs['title']
        else:
            direc = detail_soup.find("div", class_="dir_product").find("a").attrs['href']
            direc_id = int(direc.replace("/movie/bi/pi/basic.nhn?code=", ""))  # 감독 최종 id
            direc_name = detail_soup.find("div", class_="dir_product").find("a").attrs['title']

            # 인물 아이디
            peopleid = []
            for pinfo in detail_soup.find("ul", class_='lst_people').findAll("div", class_="p_info"):
                if pinfo.find("a") == None:
                    pinfo = " "
                else:
                    pinfo = pinfo.find("a").attrs['href']
                    pinfo = int(pinfo.replace("/movie/bi/pi/basic.nhn?code=", ""))
                peopleid.append(pinfo)
            peopleid.append(direc_id)  # 감독id 더해주기

            # 인물 이름
            peoplename = []
            for pinfo in detail_soup.find("ul", class_='lst_people').findAll("div", class_="p_info"):
                if pinfo.find("a") == None:
                    pinfo = pinfo.find("span").attrs['title']
                else:
                    pinfo = pinfo.find("a").attrs['title']
                peoplename.append(pinfo)
            peoplename.append(direc_name)  # 감독이름 더해주기

            # 인물 역할
            roles = [role.get_text() for role in
                     detail_soup.find("ul", class_='lst_people').findAll("em", class_="p_part")]
            roles.append("감독")  # 감독역할 더해주기

            # 인물 배역
            parts = []
            for part in detail_soup.find("ul", class_='lst_people').findAll("div", class_="part"):
                if part.find("p", class_="pe_cmt") == None:
                    part = " "
                else:
                    part = part.find('span').get_text()
                parts.append(part)
            parts.append(" ")  # 감독배역 더해주기

            # 배우, 제작진 넣을 빈 리스트 객체 만들어주기
            peoplelist = []
            forlength = len(peopleid)

            for i in range(0, forlength):
                person_id = peopleid[i]
                person_name = peoplename[i]
                role = roles[i]
                part = parts[i]

                peoplelist.append({"person_id": person_id, "person_name": person_name, "role": role, "part": part})

            movie = {"_id": movie_id,
                     "movie_id": [{"site": "naver", "id": movie_id}],
                     "movie_title": movie_title,
                     "poster": poster,
                     "director": direc_name,
                     "review_cnt": naver_review_list,  # 평점, 총 n건으로 가져오기
                     "score": [{"site": "naver", "grade": grade}],
                     "person": peoplelist,
                     "gender_ratio": [{"site": "naver", "male": male}],
                     "age": agedictlist
                     }
            naver_movie_info.save(movie)
            print(movie)

    n = n+1



