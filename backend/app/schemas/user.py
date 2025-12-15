from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    student_id: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True