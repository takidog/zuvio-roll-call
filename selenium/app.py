from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
import requests
import logging
import time
from bs4 import BeautifulSoup
import pygame
from config import Myconfig

# 設定Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

def PlayMusic(path):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(1.0)

    while True:
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            except KeyboardInterrupt:
                logging.warning("Ctrl+C detected")
                return
def run():
    chrome_options = Options()
    if(not(Myconfig["gui"])):
        chrome_options.add_argument('--headless')

    LOGGER.setLevel(logging.WARNING)#設定selenium 紀錄層級，預設warning
    driver = webdriver.Chrome(Myconfig["driver"], options=chrome_options)

    #Login
    logging.info("進入登入頁")
    driver.get("https://irs.zuvio.com.tw/")
    driver.find_element(By.ID, "email").send_keys(Myconfig["user"])
    driver.find_element(By.ID, "password").send_keys(Myconfig["password"])

    driver.find_element(By.ID, "login_btn").submit()
    #time.sleep(3)

    driver.get(Myconfig["URL"])

    logging.info("登入成功")
    #解析原始碼
    #time.sleep(1)

    logging.info("準備開始循環")
    while True:
        PageSource = driver.page_source
        soup = BeautifulSoup(PageSource,'html.parser')
        result = soup.find("div", class_="irs-rollcall")
        logging.debug(result)

        if("準時" in str(result)):
            logging.info("Play music.")
            PlayMusic(Myconfig["music"])
            return True

        if("簽到開放中" in str(result)):
            logging.info("點名中")
            driver.find_element(By.ID, "submit-make-rollcall").click()

        else:
            logging.info("無點名資訊")
            driver.refresh()

        time.sleep(7)

    

if __name__ == "__main__":
    run()
    logging.info("選課循環階段結束")