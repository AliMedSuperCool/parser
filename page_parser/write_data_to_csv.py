import csv
import json
import os


def write_data(data):
    """
    Функция принимает словарь с данными о вузе и программах,
    затем записывает:
      - данные вуза в файл "vuz.csv"
      - данные программ в файл "programs.csv"
    Если опциональное поле отсутствует, ставится значение "no data".
    """

    path = "../data/tabiturient/"
    # # Обработка данных вуза
    # vuz_data = data.get("vuz", {})
    # vuz_fields = [
    #     "long_name",  # полное название
    #     "short_name",  # аббревиатура вуза
    #     "geolocation",  # регион
    #     "is_goverment",  # True если гос вуз
    #     "rating",  # рейтинг (буквами)
    #     "logo",  # ссылка на фото
    #     "website",  # ссылка на сайт вуза
    #     "phone_admission",  # номер приемной комиссии
    #     "phone_general",  # номер вуза
    #     "email_general",  # почтан вуза
    #     "email_admission"  # почта приемной комиссии
    #
    # ]
    # vuz_row = {field: vuz_data.get(field) for field in vuz_fields}
    #
    # # Записываем данные вуза в CSV (добавляем заголовок, если файл новый)
    # vuz_csv = os.path.join(path, "vuz.csv")
    # write_header = not os.path.exists(vuz_csv) or os.stat(vuz_csv).st_size == 0
    # with open(vuz_csv, "a", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=vuz_fields)
    #     if write_header:
    #         writer.writeheader()
    #     writer.writerow(vuz_row)
    #
    # obsh_data = data.get("obsh", {})
    # obsh_fields = [
    #     "vuz",  # полное название
    #     "obsh",  # аббревиатура вуза
    #     "info",  # регион
    #     "rating",  # True если гос вуз
    # ]
    # obsh_row = {field: obsh_data.get(field) for field in obsh_fields}
    #
    # # Записываем данные вуза в CSV (добавляем заголовок, если файл новый)
    # obsh_csv = os.path.join(path, "obsh.csv")
    # write_header = not os.path.exists(obsh_csv) or os.stat(obsh_csv).st_size == 0
    # with open(obsh_csv, "a", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=obsh_fields)
    #     if write_header:
    #         writer.writeheader()
    #     writer.writerow(obsh_row)

    # Обработка данных программ
    programs_data = data.get("programs", [])
    program_fields = [
        "direction",  # направление
        "profile",  # профиль
        "program_code",  # код программы
        "vuz",  # аббревиатура вуза
        "faculty",  # факультет
        "exams",  # набор экзаменов
        "scores",  # баллы
        "forms",  # форма обучения

    ]
    program_rows = []
    for program in programs_data:
        row = {}
        # Обязательные поля
        for field in ["direction", "profile", "program_code", "vuz", "faculty", "exams", "scores", "forms"]:
            value = program[field]

            if field == ["exams", "scores", "forms"]:
                value = json.dumps(value, ensure_ascii=False)

            row[field] = value
        program_rows.append(row)

    # Запись данных программ в CSV
    programs_csv = os.path.join(path, "programs.csv")
    write_header = not os.path.exists(programs_csv) or os.stat(programs_csv).st_size == 0
    with open(programs_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=program_fields)
        if write_header:
            writer.writeheader()
        for row in program_rows:
            writer.writerow(row)


# Пример использования функции с новым форматом профиля
if __name__ == "__main__":
    with open('../data/example.json') as f:
        data = json.load(f)
    print(data)
    write_data(data)
    print("Данные успешно записаны в файлы 'vuz.csv' и 'programs.csv'.")
