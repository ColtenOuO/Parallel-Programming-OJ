from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from typing import Optional
from app.models.user import User


class UserService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        
        if crud_user.get_by_email(db, email=user_in.email):
            raise ValueError("The user with this email already exists.")
            
        if crud_user.get_by_student_id(db, student_id=user_in.student_id):
            raise ValueError("The user with this student ID already exists.")

        user_data = user_in.dict() 
        plain_password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(plain_password)
        
        return crud_user.create(db, obj_in=user_data)
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = crud_user.get_by_email(db, email=email)

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
            
        return user