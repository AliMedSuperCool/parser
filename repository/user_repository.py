# from dataclasses import dataclass
# from typing import Optional
#
# from sqlalchemy import insert, select
#
#
# from models import UserProfile as DBUser
# from sqlalchemy.orm import Session
#
# from shema import UserCreateSchema
#
#
# @dataclass
# class UserRepository:
#     db_session: Session
#
#     def create_user(self, user: UserCreateSchema) -> DBUser:
#         query = insert(DBUser).values(
#             **user.model_dump(),
#         ).returning(DBUser.id)
#
#         with self.db_session() as session:
#             user_id: DBUser.id = session.execute(query).scalar()
#             session.flush()
#             session.commit()
#             return self.get_user(user_id)
#
#     def get_user(self, user_id: int) -> DBUser:
#         query = select(DBUser).where(DBUser.id == user_id)
#         with self.db_session() as session:
#             return session.execute(query).scalar_one_or_none()
#
#     def get_user_by_username(self, username: str) -> Optional[DBUser]:
#         user = select(DBUser).where(DBUser.username == username)
#         with self.db_session() as session:
#             return session.execute(user).scalar_one_or_none()
#
#     def get_user_by_email(self, email: str) -> Optional[DBUser]:
#         query = select(DBUser).where(DBUser.email == email)
#         with self.db_session() as session:
#             return session.execute(query).scalar_one_or_none()
