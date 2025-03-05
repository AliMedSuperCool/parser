from .utils import extract_some_inner_text, extract_inner_text, extract_element


def parse_vuz_info(soup):
    vuz_info = {}
    headers = [tag.get_text(strip=True) for tag in soup.find_all(['h2'])]
    short_name, long_name = headers[0], headers[1]


    first_a_tag = soup.find_all("a")[0]
    href_value = first_a_tag.get("href")

    icon_elem = extract_element(soup, "table", "vuzlistlogoin2")
    img = icon_elem.find("img").get("src")
    img = img.split("/")[-1]
    logo = f"https://tabiturient.ru/logovuz/{img}"

    header_content = extract_element(soup, "div", "headercontent bg2")

    geolocation = extract_inner_text(
        extract_element(header_content, 'table', 'citylink1'),
        'b')
    goverment = extract_inner_text(
        extract_element(header_content, 'table', 'tag2'),
        'b')
    rating = extract_inner_text(
        extract_element(header_content, 'td', 'ocenka'),
        'b')


    vuz_info['short_name'] = short_name
    vuz_info['long_name'] = long_name
    vuz_info['geolocation'] = geolocation
    vuz_info['is_goverment'] = goverment
    vuz_info['rating'] = rating
    vuz_info["logo"] = logo
    vuz_info["website"] = href_value

    return vuz_info