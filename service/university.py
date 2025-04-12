# import string
# from dataclasses import dataclass
# from random import random, choice
#
# from repository import UserRepository
# from service.auth import AuthService
# from shema import UserLoginSchema, UserCreateSchema
#
#
# @dataclass
# class UserService:
#     user_repository: UserRepository
#     auth_service: AuthService
#
#     def create_user(self, username: str, password: str) -> UserLoginSchema:
#         user = self.user_repository.create_user(UserCreateSchema(username=username, password=password))
#         access_token = self.auth_service.generate_token(user_id=user.id)
#         return UserLoginSchema(user_id=user.id, access_token=access_token)
