import logging
import re
import time
from typing import List
import requests
import os
from lxml import etree
#from config import Myconfig

# 設定Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def LoadConfig():
    return {
    "user": os.environ["USER"],
    "password": os.environ["PASSWD"],
    "lineNotifyToken": os.environ["LINE_NOTIFY_TOKEN"],
    "lat": os.environ["LAT"],#24.122438,
    "lng": os.environ["LNG"],#120.650394,
    "waitSec": int(os.environ["WAITSEC"]),
    "Fullmode": bool(os.environ["FULLMODE"]),
    "linyNotifyOn":bool(os.environ["LINE_NOTIFY_ON"]),
    "loop":bool(os.environ["LOOP_ON"]),
    "waitSecAfterSuccess":int(os.environ["WAIT_SEC_AFTER_CALL"])
}

def lineNotify(token, msg):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    payload = {'message': msg}
    r = requests.post(url, headers = headers, params = payload)
    return r.status_code

class zuvio:
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

    def login(self, user_mail, password):
        """Login to zuvio 'irs', if want use other service,
        you must login with sso url.
        Args:
            session ([requests.session]): request session.
            user_mail ([str]): user mail.
            password ([str]): password.
        Returns:
            [bool]: login status.
        """
        def _parse_user_secret_data(login_request):
            # get userId and accessToken.
            access_token_regex = r"var accessToken = \"(\w{0,})"
            access_token_matches = list(re.finditer(
                access_token_regex, login_request.text, re.MULTILINE))
            user_id_regex = r"var user_id = (\w{0,})"
            user_id_matches = list(re.finditer(
                user_id_regex, login_request.text, re.MULTILINE))

            if len(access_token_matches) == 1 and len(user_id_matches) == 1:
                if len(access_token_matches[0].groups()) == 1 and len(user_id_matches[0].groups()) == 1:
                    return access_token_matches[0].groups()[0], user_id_matches[0].groups()[0]
            logging.warning(msg="[Login] parse user secret error.")
            return False

        login_url = 'https://irs.zuvio.com.tw/irs/submitLogin'

        form_data = {
            'email': user_mail,
            'password': password,
            'current_language': 'zh-TW'
        }
        logging.info(msg="[Login] login request...")
        login_request = self.main_session.post(url=login_url, data=form_data)

        if login_request.status_code == 200 and len(login_request.history) > 1:
            _user_secret = _parse_user_secret_data(login_request)
            if _user_secret is not False:
                self.access_token, self.user_id = _user_secret
                logging.info(msg="[Login] login success.")

                return True
        logging.warning(msg="[Login] login erorr.")

        return False

    #Get current course
    def get_course_list(self):
        """Get course list.
        Returns:
            [list]: item: dict
                    semester_id	String	28
                    semester_name	String	108-1
                    teacher_name	String	張俊....
                    course_id	String	384840
                    course_name	String	4696_1081_實務....
                    course_unread_num	String	0
                    course_created_at	String	2019-09-13 04:20:53
                    pinned	Boolean	false
        """
        course_list_url = 'https://irs.zuvio.com.tw/course/listStudentCurrentCourses'
        if self.user_id is None and self.access_token is None:
            return False
        params = {
            'user_id': self.user_id,
            'accessToken': self.access_token
        }
        logging.info(msg="[Courses] course list request.")
        course_request = self.main_session.get(course_list_url, params=params)
        if course_request.status_code == 200:
            self.course_list = course_request.json()['courses']
            logging.info(msg="[Courses] get courses success.")
            return course_request.json()['courses']
        return False

    #Get Full course
    def get_Fullcourse_list(self):

        course_list_url = 'https://irs.zuvio.com.tw/course/listStudentFullCourses'
        if self.user_id is None and self.access_token is None:
            return False
        params = {
            'user_id': self.user_id,
            'accessToken': self.access_token
        }
        logging.info(msg="[Courses] course list request.")
        course_request = self.main_session.get(course_list_url, params=params)
        if course_request.status_code == 200:
            for semester in course_request.json()['semesters']:
                for course in semester["courses"]:
                    self.course_list.append(course)

            logging.info(msg="[Courses] get courses success.")
            
            return course_request.json()['semesters'][0]['courses']
        return False

    def check_rollcall_status(self, course_id):

        def _parse_rollcall_page(html):
            "var rollcall_id = '(\w{0,})"
            root = etree.HTML(html)
            ststus_message = root.xpath(
                "//div[@class='irs-rollcall']//div[@class='text']")
            if len(ststus_message) == 1:
                logging.debug(
                    msg='[Rollcall] status {course_id} {status}'.format(
                        course_id=course_id,
                        status=ststus_message[0].text
                    ))
                if ststus_message[0].text == '目前未開放簽到':
                    return False
            return True

        def _parse_rollcall_id(html):
            rollcall_regex = r"var rollcall_id = '(\w{0,})"
            rollcall_matches = list(re.finditer(
                rollcall_regex, html, re.MULTILINE))
            if len(rollcall_matches) == 1:
                if len(rollcall_matches[0].groups()) == 1:
                    return rollcall_matches[0].groups()[0]
            return False
        rollcall_url = 'https://irs.zuvio.com.tw/student5/irs/rollcall/{course_id}'.format(
            course_id=course_id)
        rollcall_request = self.main_session.get(url=rollcall_url)
        rollcall_request.encoding = 'utf-8'
        if rollcall_request.status_code == 200:
            logging.debug(msg="[Rollcall] get {course_id} success.".format(
                course_id=course_id))
            return {
                'rollcall_status_msg': _parse_rollcall_page(rollcall_request.text),
                'rollcall_id': _parse_rollcall_id(rollcall_request.text)
            }
        return False

    def rollcall(self, rollcall_id):

        data = {
            'user_id': self.user_id,
            'accessToken': self.access_token,
            'rollcall_id': rollcall_id,
            'device': "WEB",
            'lat': self.rollcall_data['lat'],
            'lng': self.rollcall_data['lng']
        }
        rollcall_url = 'https://irs.zuvio.com.tw/app_v2/makeRollcall'
        rollcall_request = self.main_session.post(url=rollcall_url, data=data)
        if rollcall_request.status_code == 200:
            return True
        return False

    def rollcall_run_forever(self, check_sleep_sec=3):
        logging.info("[rollcall] Set wait time to " + str(check_sleep_sec))
        if len(self.course_list) == 0 :
            if(self.Fullmode):
                self.get_Fullcourse_list()
            else:
                self.get_course_list()

        logging.debug(self.course_list)
        while True:
            logging.info("check rollcall")
            for course in self.course_list:
                rollcall_status = self.check_rollcall_status(course_id=course['course_id'])
                if isinstance(rollcall_status, dict):
                    if rollcall_status['rollcall_status_msg'] != False:
                        if self.rollcall(rollcall_id=rollcall_status['rollcall_id']):
                            logging.info(msg='[OK] success rollcall. => ' + course['course_name'])
                            return course['course_name']
            time.sleep(check_sleep_sec)


if __name__ == "__main__":
    Myconfig = object
    try:
        Myconfig = LoadConfig()
    except FileNotFoundError as identifier:
        logging.fatal("Config file not found!")
        input()

    zuvio_user = zuvio(
        user_mail=Myconfig["user"],
        password=Myconfig["password"],
        Fullmode=Myconfig["Fullmode"]
    )
    #CSMU = 24.122438, 120.650394
    zuvio_user.rollcall_data = {
        'lat': Myconfig["lat"],
        'lng': Myconfig["lng"]
    }
    
    isLoop = True
    while(isLoop):
        isLoop = Myconfig["loop"] #是否循環

        courseName = zuvio_user.rollcall_run_forever(check_sleep_sec=Myconfig["waitSec"])
        
        if(Myconfig["linyNotifyOn"]):
            logging.info("[Line] notifying...")
            lineNotify(Myconfig["lineNotifyToken"], "{0} zuvio 點名中!!!".format(courseName))
        
        if(isLoop):
            logging.info("Wait for {} sec to start next loop".format(Myconfig["waitSecAfterSuccess"]))
            time.sleep(Myconfig["waitSecAfterSuccess"])
