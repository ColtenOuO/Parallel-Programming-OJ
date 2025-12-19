from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class JudgeType(str, Enum):
    standard = "standard"
    special = "special"

# =======================
# TestCase Schemas
# =======================

class TestCaseBase(BaseModel):
    input_path: str
    output_path: str
    is_sample: bool = False
    score: int = Field(default=100, ge=0)
    order: int = 0

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseUpdate(BaseModel):
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    is_sample: Optional[bool] = None
    score: Optional[int] = None
    order: Optional[int] = None

class TestCase(TestCaseBase):
    id: UUID
    problem_id: UUID

    class Config:
        from_attributes = True


# =======================
# Problem Schemas
# =======================

class ProblemBase(BaseModel):
    problem_key: str = Field(..., description="題目代號，例如 A, B, HW1_P1", min_length=1)
    
    title: str
    description: str
    problem_tags: str
    is_public: bool = False
    
    time_limit: int = 1000
    memory_limit: int = 128
    core_number: int = 1
    
    compile_command: Optional[str] = None
    compile_command: Optional[str] = None
    run_command: str
    
    judge_type: JudgeType = JudgeType.standard
    judge_script: Optional[str] = None

    @field_validator('judge_script')
    def check_script_if_special(cls, v, values):
        return v # TODO: check script if special

class ProblemCreate(ProblemBase):
    pass

class ProblemUpdate(BaseModel):
    problem_key: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    problem_tags: Optional[str] = None
    is_public: Optional[bool] = None
    
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    core_number: Optional[int] = None
    
    compile_command: Optional[str] = None
    run_command: Optional[str] = None
    
    judge_type: Optional[JudgeType] = None
    judge_script: Optional[str] = None

class ProblemSummary(BaseModel):
    id: UUID
    problem_key: str
    title: str
    problem_tags: str
    is_public: bool
    
    class Config:
        from_attributes = True

class Problem(ProblemBase):
    id: UUID
    
    test_cases: List[TestCase] = [] 

    class Config:
        from_attributes = True