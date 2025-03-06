import re
from bs4 import BeautifulSoup


# Открываем и читаем HTML-файл
def parse_obsh(html_content):
    # Создаем объект BeautifulSoup с использованием парсера lxml
    soup = BeautifulSoup(html_content, 'html.parser')

    alternate_name_tag = soup.find("h2", itemprop="alternateName").text

    header_block = soup.find("div", class_="headercontent bg1")
    additional_info_block = header_block.get_text(separator="\n", strip=True) if header_block else None

    dorm_info_div = soup.find("div", class_="p40 pm40", style=lambda v: v and "background:#ffffff" in v)
    dorm_info_text = dorm_info_div.get_text(separator="\n", strip=True) if dorm_info_div and dorm_info_div.get_text(
        separator="\n", strip=True) else None

    # Определяем наличие общежития по ключевой фразе в извлеченном тексте
    if dorm_info_text is not None:
        has_dorm = "есть общежитие" in dorm_info_text.lower()
    elif additional_info_block is not None:
        has_dorm = False if "нет общежития" in additional_info_block.lower() else None
    else:
        has_dorm = None

    if dorm_info_text:
        match = re.search(r"Оценка общежития:\s*([\d\.]+)\/10", dorm_info_text) if dorm_info_text else None
        rating = float(match.group(1)) if match else None

        dorm_info_text = re.sub(r"В этом вузе есть общежитие", "", dorm_info_text, flags=re.IGNORECASE)
        dorm_info_text = re.sub(r"Оценка общежития:\s*([\d\.]+)\/10", "", dorm_info_text, flags=re.IGNORECASE)
        dorm_info_text.strip()

    else:
        rating = None

    result_dict = {
        "vuz": alternate_name_tag,
        "obsh": has_dorm,
        "info": dorm_info_text,
        "rating": rating
    }

    return result_dict
