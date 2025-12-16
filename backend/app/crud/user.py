from sqlalchemy.orm import Session
from app.models.user import User

def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_by_student_id(db: Session, student_id: str):
    return db.query(User).filter(User.student_id == student_id).first()

def create(db: Session, obj_in: dict):
    db_obj = User(**obj_in)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj