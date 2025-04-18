import ast
import pandas as pd
import sys
import os

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_session
from models import University, Dormitory, Program, Form


def to_int(value):
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return None


Session = get_db_session()
with Session() as session:
    vuzs = pd.read_csv('data/tabiturient/all/vuz_with_army.csv')

    print("🚀 Обработка университетов...")
    for _, vuz in vuzs.iterrows():
        uni = session.execute(
            select(University).where(University.long_name == vuz.long_name)
        ).scalar_one_or_none()

        if uni:
            uni.short_name = vuz.short_name
            uni.geolocation = vuz.geolocation
            uni.is_goverment = True if vuz.is_goverment == 1 else False
            uni.rating = None if vuz.rating < 0 else vuz.rating
            uni.logo = vuz.logo
            uni.website = vuz.website
            uni.phone_admission = ast.literal_eval(vuz.phone_admission)
            uni.phone_general = ast.literal_eval(vuz.phone_general)
            uni.email_general = ast.literal_eval(vuz.email_general)
            uni.email_admission = ast.literal_eval(vuz.email_admission)
            uni.army = vuz.army
            uni.has_dormitory = vuz.obsh
        else:
            session.add(University(
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
            ))

    session.commit()

    print("\n🏢 Обработка общежитий...")
    obshs = pd.read_csv('data/tabiturient/all/osbh_all.csv')
    for _, obsh in obshs.iterrows():
        uni = session.execute(
            select(University.id).where(University.long_name == obsh.long_name)
        ).scalar_one_or_none()

        if not uni:
            print(f"⚠️ Университет не найден для общежития: {obsh.long_name}")
            continue

        dorm = session.execute(
            select(Dormitory).where(Dormitory.university_id == uni)
        ).scalar_one_or_none()

        if dorm:
            dorm.info = str(obsh.information) if obsh.information else None
            dorm.rating = float(obsh.rating) if obsh.rating else None
        else:
            session.add(Dormitory(
                university_id=uni,
                info=str(obsh.information) if obsh.information else None,
                rating=float(obsh.rating) if obsh.rating else None,
            ))

    session.commit()

    print("\n📘 Обработка программ...")
    programs = pd.read_csv('data/tabiturient/all/programs_combined.csv')

    for _, program in programs.iterrows():
        uni_id = session.execute(
            select(University.id).where(University.long_name == program.vuz)
        ).scalar_one_or_none()

        if not uni_id:
            print(f"⚠️ Университет не найден: {program.vuz}")
            continue

        existing_program = session.execute(
            select(Program).where(and_(
                Program.university_id == uni_id,
                Program.direction == program.direction,
                Program.profile == program.profile,
                Program.program_code == program.program_code,
                Program.faculty  == program.faculty,
            ))
        ).scalar_one_or_none()

        if existing_program:
            existing_program.exams = ast.literal_eval(program.exams)
            program_id = existing_program.id
        else:
            new_program = Program(
                university_id=uni_id,
                direction=program.direction,
                profile=program.profile,
                program_code=program.program_code,
                faculty=program.faculty,
                exams=ast.literal_eval(program.exams)
            )
            session.add(new_program)
            session.flush()
            program_id = new_program.id

        forms_data = ast.literal_eval(program.forms)
        for form in forms_data:
            form_name = form.get("education_form2", "").strip()

            existing_form = session.execute(
                select(Form).where(and_(
                    Form.program_id == program_id,
                    Form.education_form2 == form_name
                ))
            ).scalar_one_or_none()

            if existing_form:
                existing_form.score = to_int(form.get("score"))
                existing_form.price = to_int(form.get("price"))
                existing_form.olympic = form.get("olympic")
                existing_form.free_places = to_int(form.get("free_places"))
                existing_form.average_score = to_int(form.get("average_score", ""))
            else:
                session.add(Form(
                    program_id=program_id,
                    education_form2=form_name,
                    score=to_int(form.get("score")),
                    price=to_int(form.get("price")),
                    olympic=form.get("olympic"),
                    free_places=to_int(form.get("free_places")),
                    average_score=to_int(form.get("average_score", ""))
                ))

    try:
        session.commit()
        print("\n✅ Все изменения успешно сохранены.")
    except SQLAlchemyError as e:
        print(f"❌ Ошибка при финальном коммите: {e}")
        session.rollback()
