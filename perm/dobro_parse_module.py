import requests
import time
from bs4 import BeautifulSoup as bs


def dobro_parse(search_words):
    def get_response(url):
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            time.sleep(2)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }
    params = {'city': 'any', 'recipient': 'all', 'query': (search_words,)}

    main_url = 'https://dobro.mail.ru'
    url = 'https://dobro.mail.ru/funds/search/'

    response = get_response(url)
    soup = bs(response.text, 'html.parser')

    if soup.find_all(class_='link_font_large'):
        funds_list = soup.find_all(class_='link_font_large')
        fund_link = main_url + funds_list[0].attrs['href']

        fund_link_response = get_response(fund_link)
        fund_soup = bs(fund_link_response.text, 'html.parser')

        fund_info_dict = {'name': soup.find_all(class_='link__text')[0].text,
                          'phone': fund_soup.find_all(class_='p-fund-detail__info-cell')[1].text,
                          'url': fund_soup.find_all(class_='p-fund-detail__info-cell')[3].text}
        inn_status = 'Есть совпадение!'
    else:
        fund_info_dict = {}
        inn_status = 'Нет совпадения!'

    return fund_info_dict, inn_status
    # return inn_status