import requests
from bs4 import BeautifulSoup
import re

def get_contacts_from_url(url):
    """
    @return 
    {
        phone_admission,
        email_admission,
        phone_general,
        email_general
    }
    одно из полей или несколько
    """
    try:
        # Загрузка страницы
        response = requests.get(url)
        if response.status_code != 200:
            return "Сайт недоступен"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Шаблоны
        phone_pattern = r"(\+7|8)\s?(?:\()?(\d{3})(?:\))?\s?\d{3}-?\d{2}-?\d{2}|(\+7|8)\s?800\s?\d{3}\s?\d{4}"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        
        # Ключевые слова
        keywords_admission = ["приемная комиссия", "абитуриентам", "поступление"]
        keywords_general = ["контакты", "телефон", "email", "администрация"]
        
        phones = []
        emails = []
        
        # Поиск в тексте и ссылках
        for tag in soup.find_all(['p', 'div', 'a']):
            text = tag.get_text().lower()
            
            # Телефон
            phone_match = re.search(phone_pattern, tag.get_text())
            if phone_match:
                if any(keyword in text for keyword in keywords_admission):
                    phones.append(("admission", phone_match.group()))
                elif any(keyword in text for keyword in keywords_general):
                    phones.append(("general", phone_match.group()))
            
            # Почта
            email_match = re.search(email_pattern, tag.get_text())
            if not email_match and tag.get('href', '').startswith('mailto:'):
                email_match = re.search(email_pattern, tag.get('href'))
            if email_match:
                if any(keyword in text for keyword in keywords_admission):
                    emails.append(("admission", email_match.group()))
                elif any(keyword in text for keyword in keywords_general):
                    emails.append(("general", email_match.group()))
        
        # Приоритизация и вывод
        result = {}
        if phones:
            for type_contact, number in phones:
                if type_contact == "admission":
                    result["phone_admission"] = number
                    break
            else:
                result["phone_general"] = phones[0][1]
        
        if emails:
            for type_contact, email in emails:
                if type_contact == "admission":
                    result["email_admission"] = email
                    break
            else:
                result["email_general"] = emails[0][1]
        
        if not result:
            return "Контакты не найдены"
        return result
    except Exception as e:
        print(f"ERROR IN PARSING {url}: {e}")
        return {}
        