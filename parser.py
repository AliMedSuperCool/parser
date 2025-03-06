import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from page_parser import parse_page, parse_obsh
from write_data_to_csv import write_data

st_accept = "text/html"
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
    "Accept": st_accept,
    "User-Agent": st_useragent
}


def get_html_content(url: str) -> str:
    req = requests.get(url, headers)
    src = req.text
    return src


def parse():
    data_links = pd.read_csv('data/vizu_lins.csv')
    for index, data_link in data_links.iterrows():
        link_proxodnoi = data_link[0]
        html_content = get_html_content(link_proxodnoi)
        data = parse_page(html_content)

        link_obsh = link_proxodnoi.replace('proxodnoi', 'obsh')
        html_content = get_html_content(link_obsh)
        res_obsh = parse_obsh(html_content)
        data['obsh'] = res_obsh

        write_data(data)
        print(index)
        time.sleep(10)


if __name__ == '__main__':
    parse()
