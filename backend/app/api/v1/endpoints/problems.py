from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.ProblemSummary])
def read_problems(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    取得所有題目 (不包含詳細敘述與測資)
    """
    problems = crud.problem.get_all(db, skip=skip, limit=limit)
    return problems

@router.post("/", response_model=schemas.Problem)
def create_problem(
    *,
    db: Session = Depends(deps.get_db),
    problem_in: schemas.ProblemCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    建立新題目 (需要登入)
    """

    if crud.problem.get_by_problem_key(db, problem_key=problem_in.problem_key):
        raise HTTPException(
            status_code=400,
            detail="Problem key already exists (e.g. 'A' or 'HW1_P1' is taken)."
        )
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")


    problem = crud.problem.create(db=db, obj_in=problem_in)
    return problem

@router.get("/{problem_id}", response_model=schemas.Problem)
def read_problem(
    *,
    db: Session = Depends(deps.get_db),
    problem_id: UUID,
):
    """
    根據 ID 取得題目資料 (包含 description 與 test_cases)
    """
    problem = crud.problem.get_by_id(db, problem_id=problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.put("/{problem_id}", response_model=schemas.Problem)
def update_problem(
    *,
    db: Session = Depends(deps.get_db),
    problem_id: UUID,
    problem_in: schemas.ProblemUpdate,
    current_user: User = Depends(deps.get_current_user), # 必須登入
):
    """
    更新題目資訊
    """
    problem = crud.problem.get_by_id(db, problem_id=problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if problem_in.problem_key and problem_in.problem_key != problem.problem_key:
        if crud.problem.get_by_problem_key(db, problem_key=problem_in.problem_key):
             raise HTTPException(status_code=400, detail="Problem key already exists.")

    problem = crud.problem.update(db=db, db_obj=problem, obj_in=problem_in)
    return problem

@router.delete("/{problem_id}", response_model=schemas.Problem)
def delete_problem(
    *,
    db: Session = Depends(deps.get_db),
    problem_id: UUID,
    current_user: User = Depends(deps.get_current_user),
):
    """
    刪除題目
    """
    problem = crud.problem.get_by_id(db, problem_id=problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    problem = crud.problem.delete(db=db, db_obj=problem)
    return problem
