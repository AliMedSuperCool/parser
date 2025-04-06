# Пример использования сессии
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_session
from models import University, Dormitory, Program

Session = get_db_session()
with Session() as session:
    vuzs = pd.read_csv('data/tabiturient/all/vuz_with_army.csv')

    for num, vuz in vuzs.iterrows():
        print(f"{vuz.long_name}")
        uni = University(
            long_name=vuz.long_name,
            short_name=vuz.short_name,
            geolocation=vuz.geolocation,
            is_goverment=True if vuz.is_goverment == 1 else False,
            rating=None if vuz.rating < 0 else vuz.rating,
            logo=vuz.logo,
            website=vuz.website,
            phone_admission=eval(vuz.phone_admission),
            phone_general=eval(vuz.phone_general),
            email_general=eval(vuz.email_general),
            email_admission=eval(vuz.email_admission),
        )
        session.add(uni)
    session.commit()
    # print(f"{vuz.long_name} успешно добавлен в БД!")

    obshs = pd.read_csv('data/tabiturient/all/osbh_all.csv')
    for num, obsh in obshs.iterrows():
        print(obsh)
        dorm = Dormitory(
            vuz_long_name=obsh.long_name,
            dormitory=obsh.obsh,
            info=str(obsh.information) if obsh.information else None,
            rating=float(obsh.rating) if obsh.rating else None,
        )
        session.add(dorm)
    session.commit()
    # session.close()

    programs = pd.read_csv('data/tabiturient/processed_data/programs_cleaned.csv')
    for num, program in programs.iterrows():
        forms_data = eval(program.forms)
        # Проходим по каждому словарю в списке forms и делаем price положительным
        for i in range(len(forms_data)):
            form = forms_data[i]
            if 'price' in form and isinstance(form['price'], (int, float)):
                forms_data[i]['price'] = abs(form['price'])  # Убираем отрицательный знак

        new_program = Program(
            direction=program.direction,
            profile=program.profile,
            program_code=program.program_code,
            vuz_long_name=program.vuz,

            faculty=program.faculty,

            exams=eval(program.exams),

            scores=eval(program.scores),
            forms=forms_data,
        )

        # Добавляем объект в сессию и коммитим изменения
        session.add(new_program)

    session.commit()
