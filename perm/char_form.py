from tkinter import *
import os, shelve
import requests
import time
from bs4 import BeautifulSoup as bs
from dobro_parse_module import dobro_parse
from nalog_parse_module import nalog_parse

model_percantage='85%'
data = None


def all_search():
    global data_name,data_inn
    # Change to Toplevel (a popup) instead of a new Tk instance
    root.title('Проверка благотворительных организаций')
    Label(root, text = 'Введите ИНН организации').grid(sticky = W, columnspan = 2)
    data_inn = Text(root, width = 55, height = 2, wrap = WORD)
    data_inn.grid(sticky = W, columnspan = 2)
    Label(root, text='Введите Название организации').grid(sticky=W, columnspan=2)
    data_name = Text(root, width=55, height=2, wrap=WORD)
    data_name.grid(sticky=W, columnspan=2)


    Button(root, text = 'Submit', command = check_data).grid(row = 10, column = 0, sticky = W + E)
    Button(root, text = 'Cancel', command = root.destroy).grid(row = 10, column = 1, sticky = W + E)

def data_window_feedback():
    global data_name,data_inn
    root.title('Результаты проверки:')
    Label(root, text='Проверка ИНН').grid(sticky=W, columnspan=2)
    Label(root, text=inn_checked).grid(sticky=W, columnspan=2)
    Label(root, text='Проверка сайта').grid(sticky=W, columnspan=3)
    Label(root, text=name_checked).grid(sticky=W, columnspan=3)
    #Label(root, text='Благотворительный фонд соответствует требованиям на ').grid(sticky=W, columnspan=4)
    #Label(root, text=model_percantage).grid(sticky=W, columnspan=4)

def check_data():
    global data_name,data_inn
    global var_name,var_inn, name_checked,inn_checked
    var_name = (data_name.get(1.0, END))
    var_inn= (data_inn.get(1.0, END))
    print(var_inn,var_name)
    if data_name.get(1.0, END).strip() == '' and data_inn.get(1.0, END).strip() == '':
       print('Nothing Entered')
    else:
        name_checked=dobro_parse(var_name.split()[0])
        inn_checked=nalog_parse(var_inn.split()[0])
        data_window_feedback()
    return name_checked

def rerun():
    root.destroy()
    start()



def start():
    global root
    root = Tk()
    root.title("Проверка благотворительных фондов")
    inflam = StringVar()  # move inflam init to a broader scope so that the buttons don't but
    inflam.set('n')    # initialize it as 'n'
    root.title('')
    root.geometry('480x500')
    Button(root, text = 'Проверить компанию', command = all_search).grid(row = 1, column = 0, sticky = W)
    Button(root, text = 'Новый запрос', command = rerun,bg="blue", fg="white").grid(row = 1, column = 1, sticky = W)

    root.mainloop()

start()