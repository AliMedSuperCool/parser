import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from write_data_to_csv import write_data

st_accept = "text/html"
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
    "Accept": st_accept,
    "User-Agent": st_useragent
}


def parse_page(html_content) -> dict:
    data = {
        "vuz": {
            "long_name": "Московский государственный университет имени М.В. Ломоносова",
            "short_name": "МГУ",
            "geolocation": "Москва",
            "is_goverment": True,
            "rating": "A",
            "logo": "http://example.com/logo.png",
            "website": "http://example.com"
        },
        "programs": [
            {
                "direction": "Педагогическое образование",
                "profile": "Математическое обеспечение и администрирование",
                "program_code": "44.03.01",
                "vuz": "МГУ",
                "faculty": "Факультет Математики",
                "exams": [['РЯ'], ['M'], ['О']],
                "scores": [['139', 'заоч.']],
                "education_form": "очное",
                "free_places": 10,
                "average_score": 92.5,
                "olympic": "No data",
                "price": 200000
            }
        ]
    }

    return data


def get_html_content(url: str) -> BeautifulSoup:
    req = requests.get(url, headers)
    src = req.text
    soup = BeautifulSoup(src, 'html.parser')
    return soup


def parse():
    data_links = pd.read_csv('vizu_lins.csv')
    for index, data_link in data_links.iterrows():
        html_content = get_html_content(data_link[0])
        data = parse_page(html_content)
        write_data(data)
        print(index)
        time.sleep(10)


parse()
