import time
import re

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from .utils import extract_element, extract_inner_text, extract_some_inner_text

def parse_programs_info(soup, all_page):
    cards = ""

    if (soup.find(class_="more")):
        # URL для POST-запроса
        url = "https://tabiturient.ru/ajax/ajspec.php"
        target_div = soup.find("div", class_="mobpadd20 morediv moredivw")
        vuz_id = -1
        # Если div найден
        if target_div:
            # Извлекаем атрибут onclick
            onclick_attr = target_div.get("onclick", "")

            # Используем регулярное выражение для извлечения параметров функции showspec
            match = re.search(r"showspec\('([^']+)','([^']+)','([^']+)'", onclick_attr)

            if match:
                # Извлекаем параметры
                param1 = match.group(1)  # Первый параметр (https://tabiturient.ru)
                vuz_id = match.group(2)  # Второй параметр (7)
                param3 = match.group(3)  # Третий параметр (1)

        data = {
            "search": "",
            "bud": 0,
            "math": 1,
            "obsh": 1,
            "foreg": 1,
            "inform": 1,
            "biolog": 1,
            "geog": 1,
            "xim": 1,
            "fiz": 1,
            "lit": 1,
            "hist": 1,
            "dop": 1,
            "idvuz": vuz_id,
            "what": 1,
            "sort": 2
        }

        # Выполняем POST-запрос
        response = requests.post(url, data=data)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Оборачиваем ответ в BeautifulSoup
            cards = BeautifulSoup(response.text, "html.parser")

            # Выводим результат
        else:
            print(f"Ошибка запроса: {response.status_code}")
    else:
        element = soup.find(id='rezspec')
        inner_html = element.decode_contents()
        cards = BeautifulSoup(inner_html, "html.parser")



    modpaddcard_elements = cards.find_all("div", class_="mobpaddcard")

    specialnosti = []

    def parse_program_card(url, id):
        r = requests.post(
            url=f'{url}/ajax/ajshowmoreinfof2.php',
            data={
                'id': f"{id}"
            }
        )
        pr_card = BeautifulSoup(r.text, "html.parser")
        result = []

        main_info = extract_element(pr_card, 'div', 'bg1')
        texts = extract_some_inner_text(main_info, 'span', 'font2')
        info_types = pr_card.find_all(class_="p40 pm40")
        for info in info_types:

            if info.find(class_="table-2"):
                res = {}
                form = extract_inner_text(info, "table", "p20").split('форма обучения')[0]
                info_ege = extract_some_inner_text(info, "span", "font3")
                res['education_form2'] = form
                res['score'] = info_ege[1]
                res['free_places'] = info_ege[2]
                res['average_score'] = info_ege[3] if len(info_ege) > 3 else "no data"
                res['olympic'] = info_ege[5] if len(info_ege) > 5 else "no data"
                info_ege2 = extract_some_inner_text(info, "span", "font2")
                match = re.search(r"[-]?\d+", info_ege2[-1])

                if match:
                    cost = int(match.group())  # Преобразуем в число
                    res['price'] = cost
                else:
                    res['price'] = "no data"

                result.append(res)
        return result

    def parse_ege(circle):
        b = extract_some_inner_text(circle, 'b')
        span = extract_some_inner_text(circle, 'span', 'font0')
        new_arr = b.extend(span)
        return b

    def is_exam_name(el):
        return 'Нет' not in el and not el[0].isnumeric()

    def is_score(el):
        return el[0].isnumeric()

    for card in tqdm(modpaddcard_elements):
        texts = card.find_all('span', 'font2')
        texts = list(map(lambda el: el.get_text(strip=True), texts))

        exams = card.find_all('table', 'circ5')
        exams = list(map(lambda ex: parse_ege(ex), exams))
        specialnost = {
            'direction': texts[0],
            'education_form': texts[1].split('|')[0].strip(),
            'program_code': texts[1].split('|')[1].strip(),
            'profile': texts[2].split("Профиль:")[-1],
            'vuz': texts[4].split('|')[0].strip(),
            'faculty': texts[5].split('Подразделение:')[-1],
            'exams': list(filter(lambda el: is_exam_name(el), exams)),
            'scores': list(filter(lambda el: is_score(el), exams)),

        }
        table = card.find("table", onclick=True)

        if table:
            onclick_value = table["onclick"]

            match = re.search(r"showmoreinfof2\('([^']+)',\s*'(\d+)'\)", onclick_value)

            if match:
                extracted_url = match.group(1)  # Ссылка
                extracted_number = match.group(2)  # Число
                parsed_card = parse_program_card(extracted_url, extracted_number)
                specialnost['forms'] = parsed_card

            time.sleep(1)
        specialnosti.append(specialnost)

    return specialnosti





