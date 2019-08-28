"""
    Парсер мобильных номеров с сайта оператора TELE2
    Прямая ссылка: https://krasnoyarsk.tele2.ru/shop/number?pageParams=type%3Dchoose%26price%3D0
    Автор:
"""

import csv
import requests
import random
from time import sleep


INDEX_SEED_COUNT = 200
WAIT_BT_STEP = True


def prepare_link():
    """
    Подготовим список ссылок
    :return: list of links
    """
    url = 'https://krasnoyarsk.tele2.ru/api/shop/products/numbers/groups?indexSeed={}&siteId=siteKRASNOYARSK'

    list_of_links = []
    for i in range(1, INDEX_SEED_COUNT):
        list_of_links.append(url.format(i))
    return list_of_links


def pars_number():
    """
    Парсенр номеров из json
    :return: список спарсенных номеров
    """
    price = {}

    for link in prepare_link():
        try:
            response = requests.get(link, verify=False)
        except requests.exceptions.SSLError as e:
            price['ERROR'] = e
            continue
        except requests.exceptions.ReadTimeout as e:
            price['ERROR'] = e
            continue

        if response.status_code == 200:
            for data_line in response.json()['data']:
                amount = data_line['price']['amount']
                if amount not in price:
                    price[amount] = set()

                val_link = price.get(amount)

                for number in data_line['bundleGroups'][0]['bundles']:
                    val_link.add(number['numbers'][0]['number'])

            print(f'Обработана ссылка: {link}')
        else:
            price['ERROR'] = f"Ошибка получения данных по ссылке {link}\n" \
                             f"Сервер вернул статус {response.status_code}"

        if WAIT_BT_STEP:
            sleep(random.randint(5, 10))

    return price


def save_in_file(result):
    """
    Write result to a CSV file
    """
    fieldname = ('Cost_number', 'Number')

    with open('output.csv', 'w', newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fieldname)
        for key in result.keys():
            for val in result.get(key):
                writer.writerow((key, val))


if __name__ == '__main__':
    result_of_pars = pars_number()
    if 'ERROR' in result_of_pars and len(result_of_pars) == 1:
        print('Опаньки... ничего не выбрали... =( ')
    else:
        save_in_file(result_of_pars)