from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.problem import TestCase
from app.schemas.problem import TestCaseCreate, TestCaseUpdate

def get_multi_by_problem(
    db: Session, problem_id: UUID, skip: int = 0, limit: int = 100
) -> List[TestCase]:
    return (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem_id)
        .order_by(TestCase.order)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create(db: Session, obj_in: TestCaseCreate, problem_id: UUID) -> TestCase:
    db_obj = TestCase(
        **obj_in.model_dump(),
        problem_id=problem_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, id: UUID) -> TestCase:
    obj = db.query(TestCase).get(id)
    db.delete(obj)
    db.commit()
    return obj