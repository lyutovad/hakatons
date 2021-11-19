# -*- coding: utf-8 -*-
import datetime
import config
import telebot
from telebot import types
from threading import Thread
import schedule
import uuid
import time

import tg_analytic
import uk
from db import add_to_db_tasklist, read_data_in_task, delete_task, init_db, change_tz, get_user_tz, get_chatid_by_date

bot = telebot.TeleBot(config.token)

keyboard = types.ReplyKeyboardMarkup(True, True)

def generate_keyboard(*answer):
    for item in answer:
        button = types.KeyboardButton(item)
        keyboard.add(button)
    return keyboard

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    tg_analytic.statistics(message.chat.id, message.text)
    keyboard = generate_keyboard('Узнать управляющую компанию', 'Распознать показания счетчиков(in test)', 'Напомнить о подаче показаний')
    tz_string = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
    bot.send_message(message.chat.id,
                    f"Привет, я бот для помощи подачи показаний.\n"
                    f"Что умею: Добавить напоминание о сдачи показаний, узнать управляющую компанию по адресу и распознать показания счетчиков(beta)\n"
                    f"Текущий часовой пояс:{tz_string}", reply_markup=keyboard)

@bot.message_handler(commands=['tasklist'])  # Функция отвечает на комнаду tasklist
def start_message(message):
    tg_analytic.statistics(message.chat.id, message.text)
    text = read_data_in_task(message.chat.id)
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(content_types=["text"])
def check_text_message(message):
    if message.text[:13] == 'статистика245' or message.text[:13] == 'Cтатистика245':
        st = message.text.split(' ')
        if 'txt' in st or 'тхт' in st:
            tg_analytic.analysis(st,message.chat.id)
            with open('%s.txt' %message.chat.id ,'r',encoding='UTF-8') as file:
                bot.send_document(message.chat.id,file)
                tg_analytic.remove(message.chat.id)
        elif(len(st) > 1):
            print('get stat')
            messages = tg_analytic.analysis(st,message.chat.id)
            bot.send_message(message.chat.id, messages)
    if message.text == 'Узнать управляющую компанию':
        tg_analytic.statistics(message.chat.id, message.text)
        sent = bot.send_message(message.chat.id, 'Введите адрес дома', reply_markup=keyboard)
        bot.register_next_step_handler(sent, uuk)
    elif message.text == 'Распознать показания счетчиков':
        tg_analytic.statistics(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Загрузите фотографию(как фото, не как файл)', reply_markup=keyboard)
    elif message.text == 'Напомнить о подаче показаний':
        tg_analytic.statistics(message.chat.id, message.text)
        sent = bot.send_message(message.chat.id, 'Введите число месяца(<29) и время в формате day 23:59. Каждое число этого месяца будет приходить напоминание', reply_markup=keyboard)
        bot.register_next_step_handler(sent, add_remind)
    else:
        tg_analytic.statistics(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Сейчас позову на помощь', reply_markup=keyboard)

@bot.message_handler(content_types=['photo'])
def handle_docs_document(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = '/home/ubuntu/mybot/mybot/data/' + message.photo[1].file_id + ".jpg"
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    num = recognite(src)
    bot.reply_to(message, num)

@bot.message_handler(commands=['timezone'])  # Функция отвечает на комнаду timezone
def timezone_message(message):
    keyboard2 = types.InlineKeyboardMarkup()
    keyboard2.add(types.InlineKeyboardButton(text='Изменить часовой пояс', callback_data='list_timezone'))
    if get_user_tz(message.chat.id) == 'none':
        bot.send_message(message.chat.id, 'Часовой пояс не установлен', reply_markup=keyboard)
    else:
        timezone = get_user_tz(message.chat.id)
        bot.send_message(message.chat.id, timezone, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)  # Реакция на кнопки
def callback(call):
    if call.data == 'list_timezone':
        list_timezone(call.message.chat.id)
    elif call.data == 'add_remind':
        add_remind(call.message)

def add_remind(message):
    msg = 'Напоминание о подачи показаний счётчиков'
    uid = uuid.uuid4()
    current_time = datetime.datetime.now(tz=None)
    

    if(len(message.text) > 8):
        bot.send_message(message.chat.id, 'Неправильный формат даты/времени. Попробуйте ещё раз', reply_markup=keyboard)
        return
    
    s = message.text.split(' ')
    
    if s[0].isdigit() is False or int(s[0]) > 28 or int(s[0]) < 1:
        bot.send_message(message.chat.id, 'Неправильное число месяца', reply_markup=keyboard)
        return
    
    st = s[1].split(':')
    if st[0].isdigit() and st[1].isdigit() is False or int(st[0]) > 23 or int(st[1]) > 59 or int(st[1]) < 0 or int(st[0]) < 0:
        bot.send_message(message.chat.id, 'Неправильное время', reply_markup=keyboard)
        return
    
    dt = set_date(current_time, int(s[0]), int(st[0]), int(st[1]))
    bot.reply_to(message, 'Напомню в следующий раз ' + str(dt.day)
                + '/' + str(dt.month) + '/' + str(dt.year) + ' в ' + str(dt.hour) + ':' + st[1], reply_markup=keyboard)

    add_to_db_tasklist(message.chat.id, dt, msg, uid)

def next_date(date, day, hour, min):
    month = date.month
    year = date.year
    
    if month < 12:
        month += 1
    else:
        month = 1
        year += 1

    date = date.replace(year=year, month=month, day=day, hour=hour, minute=min)
    return date

def set_date(date, day, hour, min):
    month = date.month
    year = date.year

    date = date.replace(year=year, month=month, day=day, hour=hour, minute=min)
    return date

def uuk(message):
    text = message.text
    print(text)
    txt, ogrn, loc_text = uk.get_uk(text)
    if txt == 'b':
        bot.send_message(message.chat.id, 'По этому адресу ничего не нашлось :(', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, txt + '\n' + ogrn + '\n' + loc_text, reply_markup=keyboard)

def recognite(fpath):
    number = 1111
    return number

def job():
    print('in job')
    current_time = datetime.datetime.now(tz=None)
    s = str(current_time.year) + '-' +\
            "{0:0=2d}".format(current_time.month) + '-' +\
            "{0:0=2d}".format(current_time.day) + ' ' +\
            "{0:0=2d}".format(current_time.hour) + ':' +\
            "{0:0=2d}".format(current_time.minute)

    uid, chatid, txt = get_chatid_by_date(s)
    if chatid == 'None':
        print('chatid is None')
        return

#   ToDo: double check
    # stext = text.split('-')
    # month = stext[1]
    # day = stext[2]
    # print(stext)
    # print(day, month)

    delete_task(uid)
    next_date

    keyboard2 = types.InlineKeyboardMarkup()
    keyboard2.add(types.InlineKeyboardButton(text='Повторить в следующем месяце в это же время', callback_data='add_remind'))
    
    bot.send_message(chatid, 'Напоминаю что нужно передать показания счётчиков', reply_markup=keyboard2)



def do_schedule():
    schedule.every().minute.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

def list_timezone(id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Europe/Moscow', callback_data='set_timezone:Europe/Moscow'))
    keyboard.add(types.InlineKeyboardButton(text='Europe/Kaliningrad', callback_data='set_timezone:Europe/Kaliningrad'),
                 types.InlineKeyboardButton(text='Europe/Samara', callback_data='set_timezone:Europe/Samara'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Yekaterinburg', callback_data='set_timezone:Asia/Yekaterinburg'),
                 types.InlineKeyboardButton(text='Asia/Omsk', callback_data='set_timezone:Asia/Omsk'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Krasnoyarsk', callback_data='set_timezone:Asia/Krasnoyarsk'),
                 types.InlineKeyboardButton(text='Asia/Irkutsk', callback_data='set_timezone:Asia/Irkutsk'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Yakutsk', callback_data='set_timezone:Asia/Yakutsk'),
                 types.InlineKeyboardButton(text='Asia/Vladivostok', callback_data='set_timezone:Asia/Vladivostok'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Magadan', callback_data='set_timezone:Asia/Magadan'),
                 types.InlineKeyboardButton(text='Asia/Kamchatka', callback_data='set_timezone:Asia/Kamchatka'))
    bot.send_message(id, 'Выберите часовой пояс', reply_markup=keyboard)

if __name__ == '__main__':
    init_db()
    thread = Thread(target=do_schedule)
    thread.start()
    bot.polling(none_stop=True) 

