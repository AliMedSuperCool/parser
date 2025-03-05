import csv
import os

def write_data(data):
    """
    Функция принимает словарь с данными о вузе и программах,
    затем записывает:
      - данные вуза в файл "vuz.csv"
      - данные программ в файл "programs.csv"
    Если опциональное поле отсутствует, ставится значение "no data".
    """

    # Обработка данных вуза
    vuz_data = data.get("vuz", {})
    vuz_fields = [
        "long_name",    # полное название
        "short_name",   # аббревиатура вуза
        "geolocation",  # регион
        "is_goverment", # True если гос вуз
        "rating",       # рейтинг (буквами)
        "logo",         # ссылка на фото
        "website"       # ссылка на сайт вуза
    ]
    vuz_row = {field: vuz_data.get(field) for field in vuz_fields}

    # Записываем данные вуза в CSV (добавляем заголовок, если файл новый)
    vuz_csv = "vuz.csv"
    write_header = not os.path.exists(vuz_csv) or os.stat(vuz_csv).st_size == 0
    with open(vuz_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=vuz_fields)
        if write_header:
            writer.writeheader()
        writer.writerow(vuz_row)

    # Обработка данных программ
    programs_data = data.get("programs", [])
    program_fields = [
        "direction",      # направление
        "profile",        # профиль
        "program_code",   # код программы
        "vuz",            # аббревиатура вуза
        "faculty",        # факультет
        "exams",          # набор экзаменов
        "scores",         # баллы
        "education_form", # форма обучения
        "free_places",    # бюджетных мест (опционально)
        "average_score",  # средний проходной балл (опционально)
        "olympic",        # количество олимпиадных мест (опционально)
        "price"           # стоимость обучения (опционально)
    ]
    program_rows = []
    for program in programs_data:
        row = {}
        # Обязательные поля
        for field in ["direction", "profile", "program_code", "vuz", "faculty", "exams", "scores", "education_form"]:
            value = program[field]

            if field == "exams":
                value = " ".join([" ".join(exams_group) for exams_group in value])

            if field == "scores":
                value = ";".join([f"{score} ({form})" for score, form in value])

            row[field] = value
        # Опциональные поля
        for field in ["free_places", "average_score", "olympic", "price"]:
            row[field] = program.get(field)
        program_rows.append(row)

    # Запись данных программ в CSV
    programs_csv = "programs.csv"
    write_header = not os.path.exists(programs_csv) or os.stat(programs_csv).st_size == 0
    with open(programs_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=program_fields)
        if write_header:
            writer.writeheader()
        for row in program_rows:
            writer.writerow(row)

# Пример использования функции с новым форматом профиля
if __name__ == "__main__":
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
                "olympic": 5,
                "price": 200000
            }
        ]
    }

    write_data(data)
    print("Данные успешно записаны в файлы 'vuz.csv' и 'programs.csv'.")
