from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemUpdate

def get_by_id(db: Session, problem_id: UUID) -> Optional[Problem]:
    return db.query(Problem).filter(Problem.id == problem_id).first()

def get_by_problem_key(db: Session, problem_key: str) -> Optional[Problem]:
    return db.query(Problem).filter(Problem.problem_key == problem_key).first()

def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Problem]:
    return db.query(Problem).offset(skip).limit(limit).all()

def create(db: Session, obj_in: ProblemCreate) -> Problem:
    db_obj = Problem(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Problem, obj_in: ProblemUpdate) -> Problem:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, db_obj: Problem) -> Problem:
    db.delete(db_obj)
    db.commit()
    return db_obj