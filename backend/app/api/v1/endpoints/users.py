from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.api import deps
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
):
    """
    Register a new user
    """
    try:
        user = UserService.register_user(db=db, user_in=user_in)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )