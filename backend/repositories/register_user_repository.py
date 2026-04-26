from fastapi.exceptions import ValidationException
from models import User, Role
from auth.utils import verify_password, get_password_hash


class RegisterUserRepository:

  def __init__(self, db):
    self.db = db

  def get_role_id_by_name(self, user_data):
    role_name = user_data.role
    # Buscar el role_id basado en el nombre del rol
    role = self.db.query(Role).filter(Role.name == role_name.value).first()
    return role.id if role else None

  def register_user_db(self, user_data):
    email_exist = self.db.query(User).filter(User.email == user_data.email).first()
    if email_exist:
      raise ValidationException("Email already registered")

    hashed_password = get_password_hash(user_data.password)
    id = self.get_role_id_by_name(user_data)
    if not id:
      raise ValidationException("Role not found")
    print(user_data.email)
   
    new_user = User(email=user_data.email,
                    hashed_password=hashed_password,
                    full_name=user_data.full_name,
                    role_id=id)

    self.db.add(new_user)
    self.db.commit()
    self.db.refresh(new_user)
    return new_user
