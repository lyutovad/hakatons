import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By


def nalog_parse(inn):
    driver = webdriver.Chrome()
    driver.get("https://egrul.nalog.ru/index.html")
    query_form = driver.find_element(By.ID, 'query')
    query_form.clear()
    query_form.send_keys(inn)

    find_button = driver.find_element(By.ID, 'btnSearch')
    find_button.click()
    time.sleep(3)

    try:
        data = driver.find_element(By.CLASS_NAME, 'res-text').text.split(',')
        data[0] = 'Адрес: ' + data[0]
    except selenium.common.exceptions.NoSuchElementException:
        data = 'нет совпадений'

    return data