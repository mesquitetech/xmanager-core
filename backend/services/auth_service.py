from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories.register_user_repository import RegisterUserRepository

class AuthService:
    def __init__(self, db):
        self.db = db
        self.repository = RegisterUserRepository(db)
      
    def register_user(self, user_data):

      result = self.repository.register_user_db(user_data)
      print(result)
      return result