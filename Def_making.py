import re
import hgtk

def FirstMiddleLast(split_word_list) :

    # 유니코드 한글 시작 : 44032, 끝 : 55199
    BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28
    # 초성 리스트. 00 ~ 18
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    # 중성 리스트. 00 ~ 20
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
                     'ㅣ']
    # 종성 리스트. 00 ~ 27 + 1(1개 없음)
    JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
                     'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    result = []
    for j in range(0, len(split_word_list)):
        # 한글 여부 check 후 분리
        char_code = ord(split_word_list[j]) - BASE_CODE  # 한 단어에 대한 ord(아스킷코드로변환) 후 초성중성나누기 위해 베이스코드 빼줌

        char1 = int(char_code / CHOSUNG)
        result.append(CHOSUNG_LIST[char1])

        char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
        result.append(JUNGSUNG_LIST[char2])

        char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
        result.append(JONGSUNG_LIST[char3])

    return result

####################################################################################################################################################################################




def word_making_function (wordlist):
    final_word=""
    j=0
    cnt = len(wordlist)
    while j<cnt:

        if wordlist[j][1] == 'ETM' and wordlist[j][0]=='ㄴ':

            test_keyword = wordlist[j-1][0]
            split_word_list = list(test_keyword)

            result = FirstMiddleLast(split_word_list)

            rotate = int(len(result) / 3)
            resultword = []

            if result[-1] == " ":  # 마지막 종성에 받침없으면
                result[-1] = 'ㄴ'
                for i in range(0, rotate):
                    resultword.extend(result[i * 3:i * 3 + 3])
                    if re.match('[ㄱ-ㅎ]', result[i * 3:i * 3 + 3][2]):
                        resultword.extend([' '])
                resultword2 = hgtk.text.compose(resultword)
                resultword2 = resultword2.replace(" ", "")  # 단어만들어진 후 이므로 깨끗하게 정리함

            elif result[5] == 'ㅂ':
                result[5] = " "
                for i in range(0, rotate):
                    resultword.extend(result[i * 3:i * 3 + 3])
                    if re.match('[ㄱ-ㅎ]', result[i * 3:i * 3 + 3][2]):
                        resultword.extend([' '])
                resultword2 = hgtk.text.compose(resultword)
                resultword2 = resultword2 + '운'
                resultword2 = resultword2.replace(" ", "")  # 단어만들어진 후 이므로 깨끗하게 정리함

            del wordlist[j]
            cnt=cnt-1

            newTuple = (resultword2, 'ttorae')

            wordlist[j-1] = newTuple

        j = j + 1


    for i in range(0, len(wordlist)):
        final_word += wordlist[i][0]

    print("final_word", final_word)











