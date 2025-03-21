from bs4 import BeautifulSoup


def extract_element(soup, tag_name, class_name):

    element = soup.find(tag_name, class_=class_name)
    inner_html = element.decode_contents()
    result = BeautifulSoup(inner_html, "html.parser")
    return result

def extract_inner_text(soup, tag_name, class_name=''):
    """
    Извлекает inner text первого найденного элемента по тегу и классу.

    :param soup: Объект BeautifulSoup, в котором производится поиск.
    :param tag_name: Имя тега (например, "div", "p", "span").
    :param class_name: Имя класса для поиска элемента.
    :return: Inner text найденного элемента, или None, если элемент не найден.
    """
    if class_name == '':
      element = soup.find(tag_name)
    else:
      element = soup.find(tag_name, class_=class_name)
    if element:
        return element.get_text(strip=True)
    return None


def extract_some_inner_text(soup, tag_name, class_name=''):
    """
    Извлекает inner text первого найденного элемента по тегу и классу.

    :param soup: Объект BeautifulSoup, в котором производится поиск.
    :param tag_name: Имя тега (например, "div", "p", "span").
    :param class_name: Имя класса для поиска элемента.
    :return: Inner text найденного элемента, или None, если элемент не найден.
    """
    if class_name == '':
      elements = soup.find_all(tag_name)
    else:
      elements = soup.find_all(tag_name, class_=class_name)
    if elements:
        return list(map(lambda el: el.get_text(strip=True), elements))
    return []