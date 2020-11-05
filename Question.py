from zuvio import zuvio, LoadConfig
import requests
import logging
import re

# 設定Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

class zuvioQuestion(zuvio):
    def __init__(self, user_mail, password, Fullmode, **kwargs):
        self.main_session = requests.session()
        self.main_session.verify = False
        self.access_token = None
        self.user_id = None
        if self.login(user_mail, password) is False:
            logging.warning(msg='Login fail')
            raise ValueError("User can't login, check your account status.")
        logging.info(msg="[Login] Login success.")
        self.course_list = list()
        if(Fullmode):
            logging.info("[init] Set mode to Full")
            self.get_Fullcourse_list()
        else:
            logging.info("[init] Set mode to Current")
            self.get_course_list()
        self.rollcall_data = {
            "lat": -79.84974,
            "lng": 7.9440943
        }

    def fetchURL(self, url):
        r = self.main_session.post(url)
        return r.text

    def fetchQuestionList(self):
        preftechList = self.get_course_list()
        courseidList = []
        for item in preftechList:
            courseidList.append(item["course_id"])

        return self.regexCheck(courseidList)

    def regexCheck(self, courseidList):
        regexStr = "GAFA_clickQuestion\('([0-9]+)','(.+)',"
        QuestionBaseUrl = "https://irs.zuvio.com.tw/student5/irs/clickers/"
        haveQuestionCourseList = []

        for courseId in courseidList:
            print(QuestionBaseUrl + courseId)
            res = self.fetchURL(QuestionBaseUrl + courseId)

            reres = re.findall(regexStr, res)
            if(reres != []):
                haveQuestionCourseList.append(reres)

        return haveQuestionCourseList

    def fetchQuestionPage(self, questionId):
        QuestionPageBaseUrl = "https://irs.zuvio.com.tw/student5/irs/clicker/"

        
if __name__ == "__main__":
    Myconfig = object
    try:
        Myconfig = LoadConfig()
    except FileNotFoundError as identifier:
        logging.fatal("Config file not found!")
        input()

    zuvio_user = zuvioQuestion(
        user_mail=Myconfig["user"],
        password=Myconfig["password"],
        Fullmode=Myconfig["Fullmode"]
    )

print(zuvio_user.fetchQuestionList())