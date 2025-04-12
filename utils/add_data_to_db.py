# Пример использования сессии
import ast

import pandas as pd
import sys
import os

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_session
from models import University, Dormitory, Program, Form

Session = get_db_session()
with Session() as session:
    vuzs = pd.read_csv('data/tabiturient/all/vuz_with_army.csv')
    try:
        for num, vuz in vuzs.iterrows():

            uni = University(
                long_name=vuz.long_name,
                short_name=vuz.short_name,
                geolocation=vuz.geolocation,
                is_goverment=True if vuz.is_goverment == 1 else False,
                rating=None if vuz.rating < 0 else vuz.rating,
                logo=vuz.logo,
                website=vuz.website,
                phone_admission=ast.literal_eval(vuz.phone_admission),
                phone_general=ast.literal_eval(vuz.phone_general),
                email_general=ast.literal_eval(vuz.email_general),
                email_admission=ast.literal_eval(vuz.email_admission),
                army=vuz.army,
                has_dormitory=vuz.obsh
            )
            session.add(uni)

            if num % 100 == 0:
                session.commit()


    except SQLAlchemyError as e:
        print(f"Ошибка при коммите: {e}")
        session.rollback()
    session.commit()
    # print(f"{vuz.long_name} успешно добавлен в БД!")

    obshs = pd.read_csv('data/tabiturient/all/osbh_all.csv')



    for num, obsh in obshs.iterrows():
        uni = session.execute(
            select(University.id).where(University.long_name == obsh.long_name)
        ).scalar_one_or_none()

        dorm = Dormitory(
            university_id=uni,
            # dormitory=obsh.obsh,
            info=str(obsh.information) if obsh.information else None,
            rating=float(obsh.rating) if obsh.rating else None,
        )
        session.add(dorm)
    try:
        session.commit()
    except SQLAlchemyError as e:
        print(f"Ошибка при коммите: {e}")
        session.rollback()

    # programs = pd.read_csv('data/tabiturient/processed_data/programs_cleaned.csv')
    # for num, program in programs.iterrows():
    #     forms_data = eval(program.forms)
    #     # Проходим по каждому словарю в списке forms и делаем price положительным
    #     for i in range(len(forms_data)):
    #         form = forms_data[i]
    #         if 'price' in form and isinstance(form['price'], (int, float)):
    #             forms_data[i]['price'] = abs(form['price'])  # Убираем отрицательный знак
    #         if "score" in form and isinstance(form['score'], (int, float, str)):
    #             try:
    #                 int(form['score'])
    #                 forms_data[i]['score'] = abs(int(form['score']))
    #             except (ValueError, TypeError, KeyError):
    #                 pass
    #
    #
    #         if "free_places" in form and isinstance(form['free_places'], (int, float,str)):
    #             try:
    #                 int(form['free_places'])
    #                 forms_data[i]['free_places'] = abs(int(form['free_places']))
    #             except (ValueError, TypeError, KeyError):
    #                 pass
    #         if "average_score" in form and isinstance(form['average_score'], (int, float,str)):
    #             try:
    #                 int(form['average_score'])
    #                 forms_data[i]['average_score'] = abs(int(form['average_score']))
    #             except (ValueError, TypeError, KeyError):
    #                 pass
    #
    #     uni = session.execute(
    #         select(University.id).where(University.long_name == program.vuz)
    #     ).scalar_one_or_none()
    #
    #     new_program = Program(
    #         university_id=uni,
    #         direction=program.direction,
    #         profile=program.profile,
    #         program_code=program.program_code,
    #         # vuz_long_name=program.vuz,
    #
    #         faculty=program.faculty,
    #
    #         exams=ast.literal_eval(program.exams),
    #         forms=forms_data,
    #     )
    #
    #     # Добавляем объект в сессию и коммитим изменения
    #     session.add(new_program)
    # try:
    #     session.commit()
    # except SQLAlchemyError as e:
    #     print(f"Ошибка при коммите: {e}")
    #     session.rollback

    programs = pd.read_csv('data/tabiturient/processed_data/programs_cleaned.csv')

    for num, program in programs.iterrows():
        try:
            # Получаем ID университета
            uni_id = session.execute(
                select(University.id).where(University.long_name == program.vuz)
            ).scalar_one_or_none()

            if uni_id is None:
                print(f"Университет не найден: {program.vuz}")
                continue

            # Создаём объект программы
            new_program = Program(
                university_id=uni_id,
                direction=program.direction,
                profile=program.profile,
                program_code=program.program_code,
                faculty=program.faculty,
                exams=ast.literal_eval(program.exams)
            )

            session.add(new_program)
            session.flush()  # Получаем ID программы до коммита

            # Разбор форм
            forms_data = ast.literal_eval(program.forms)
            for form in forms_data:
                # Приводим значения к числам, если возможно
                def to_int(value):
                    try:
                        return abs(int(value))
                    except (ValueError, TypeError):
                        return None

                new_form = Form(
                    program_id=new_program.id,
                    education_form2=form.get("education_form2", "").strip(),
                    score=to_int(form.get("score")),
                    price=to_int(form.get("price")),
                    olympic=form.get("olympic"),
                    free_places=to_int(form.get("free_places")),
                    average_score=to_int(form.get("average_score", ""))
                )
                session.add(new_form)

        except Exception as e:
            print(f"Ошибка при обработке строки {num}: {e}")
            session.rollback()

    try:
        session.commit()
    except SQLAlchemyError as e:
        print(f"Ошибка при коммите: {e}")
        session.rollback()