import requests
from bs4 import BeautifulSoup
import re


def extract_contacts_from_section(section, keywords_admission, keywords_general, phone_pattern, email_pattern):
    """
    Извлекает номера телефонов и email из указанного участка (section) HTML.
    Возвращает два списка: phones и emails, где каждый элемент - кортеж (тип, значение).
    """
    phones = []
    emails = []

    if section:
        # Ищем в тегах, где обычно располагается контактная информация
        for tag in section.find_all(['p', 'div', 'a']):
            text = tag.get_text().lower()
            # Поиск телефона
            phone_match = re.search(phone_pattern, tag.get_text())
            if phone_match:
                if any(keyword in text for keyword in keywords_admission):
                    phones.append(("admission", phone_match.group()))
                elif any(keyword in text for keyword in keywords_general):
                    phones.append(("general", phone_match.group()))

            # Поиск email
            email_match = re.search(email_pattern, tag.get_text())
            # Если email не найден в тексте, проверяем атрибут href для mailto:
            if not email_match and tag.get('href', '').startswith('mailto:'):
                email_match = re.search(email_pattern, tag.get('href'))
            if email_match:
                if any(keyword in text for keyword in keywords_admission):
                    emails.append(("admission", email_match.group()))
                elif any(keyword in text for keyword in keywords_general):
                    emails.append(("general", email_match.group()))
    return phones, emails


def get_contacts_from_url(url):
    """
    Извлекает контактную информацию (номера телефонов и email-адреса) с веб-страницы,
    классифицируя их по тематике: "admission" (приёмная комиссия) и "general" (общие контакты).

    Алгоритм:
    1. Поиск контактов в секциях header и footer.
    2. Если контакты не найдены, поиск по всему документу.

    Возвращает словарь с найденными контактами или сообщение об ошибке/отсутствии контактов.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Сайт недоступен"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Регулярные выражения для поиска номеров телефонов и email-адресов
        phone_pattern = (
            r"(?:\+7|8)\s*(?:\(?\d{3,4}\)?)\s*(?:\d{3}-?\d{2}-?\d{2}|\d{2}-?\d{2}-?\d{2})"
            r"|(?:\+7|8)\s*800\s*\d{3}\s*\d{4}"
        )
        # phone_pattern = r"(\+7|8)\s?(?:\()?(\d{3,4})(?:\))?\s?\d{2,3}-?\d{2}-?\d{2}|(\+7|8)\s?800\s?\d{3}\s?\d{4}"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Ключевые слова для классификации контактов
        keywords_admission = ["приемная комиссия", "приёмная комиссия", "абитуриентам", "поступление"]
        keywords_general = ["контакты", "телефон", "email", "администрация", "главный корпус", "реквизиты университета",
                            "телефонный справочник"]

        phones = []
        emails = []

        # Сначала ищем в header и footer
        header_section = soup.find('header')
        footer_section = soup.find('footer')

        header_phones, header_emails = extract_contacts_from_section(header_section, keywords_admission,
                                                                     keywords_general, phone_pattern, email_pattern)
        footer_phones, footer_emails = extract_contacts_from_section(footer_section, keywords_admission,
                                                                     keywords_general, phone_pattern, email_pattern)

        phones.extend(header_phones)
        phones.extend(footer_phones)
        emails.extend(header_emails)
        emails.extend(footer_emails)

        # Если ничего не найдено в header/footer, ищем по всему документу
        if not phones and not emails:
            page_phones, page_emails = extract_contacts_from_section(soup, keywords_admission, keywords_general,
                                                                     phone_pattern, email_pattern)
            phones.extend(page_phones)
            emails.extend(page_emails)

        # Приоритизация контактов: предпочтение отдано информации для приема
        result = {"phone_admission": [],
                  "phone_general": [],
                  "email_general": [],
                  "email_admission": []}
        phones = list(set(phones))
        emails = list(set(emails))
        if phones:
            for contact_type, number in phones:
                if contact_type == "admission":
                    result["phone_admission"].append(number)

                elif contact_type == "general":
                    result["phone_general"].append(number)

        if emails:
            for contact_type, email in emails:
                if contact_type == "admission":
                    result["email_admission"].append(email)
                elif contact_type == "general":
                    result["email_general"].append(email)

        if not result:
            return None
        return result

    except Exception as e:
        print(f"ERROR IN PARSING {url}: {e}")
        return {}


# Пример вызова функции
if __name__ == "__main__":
    url = "https://mrsu.ru/ru/"
    contacts = get_contacts_from_url(url)
    print(contacts)
