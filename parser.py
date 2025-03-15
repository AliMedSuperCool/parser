import time
import pandas as pd
import requests
import logging

from page_parser import parse_page, parse_obsh, get_contacts_from_url
from write_data_to_csv import write_data


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'uk,en-US;q=0.9,en;q=0.8,ru;q=0.7',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}

# Настраиваем логирование: ошибки будут записываться в файл error.log
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_html_content(url: str) -> str:
    req = requests.get(url, headers)
    src = req.text
    return src


def parse():
    data_links = pd.read_csv('data/vizu_lins.csv')
    for index, data_link in data_links.iterrows():
        try:
            # Обработка данных для proxodnoi
            link_proxodnoi = data_link[0]
            html_content = get_html_content(link_proxodnoi)
            data = parse_page(html_content)

            # Обработка данных для obsh
            # link_obsh = link_proxodnoi.replace('proxodnoi', 'obsh')
            # html_content = get_html_content(link_obsh)
            # res_obsh = parse_obsh(html_content)
            # data['obsh'] = res_obsh
            # if data['vuz']['website'] is not None:
            #     contact_info = get_contacts_from_url(data['vuz']['website'])
            #     if contact_info is not None:
            #         data['vuz'] = {**data['vuz'], **contact_info}

            write_data(data)
            print(f"Итерация {index} {data_link[0]} успешно обработана")
        except Exception as e:
            print(f"Ошибка на итерации {index} {data_link[0]}")

            logging.exception(f"Ошибка на итерации {index} {data_link[0]}: {e}")
        # Ждем 10 секунд перед следующей итерацией
        time.sleep(7)



if __name__ == '__main__':
    parse()
