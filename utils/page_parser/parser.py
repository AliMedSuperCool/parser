from bs4 import BeautifulSoup
from utils.page_parser.parse_programs_info import parse_programs_info

def parse_page(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    main_content_div = soup.find("div", class_="maincontent")

    inner_html = main_content_div.decode_contents()
    soup = BeautifulSoup(inner_html, "html.parser")

    # vuz_info = parse_vuz_info(soup)
    # print("parsed vuz_info")

    #======================================

    programs = parse_programs_info(soup)
    print("parsed programs_info")

    RESULT = {
        # 'vuz': vuz_info,
        'programs': programs
    }

    return RESULT
