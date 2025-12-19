import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Problem(Base):
    __tablename__ = "problem"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    title = Column(String, nullable=False)
    problem_key = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    problem_tags = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    
    time_limit = Column(Integer, default=1000)
    memory_limit = Column(Integer, default=128)
    core_number = Column(Integer, default=1)
    
    compile_command = Column(String, nullable=True) 
    run_command = Column(String, nullable=False)

    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")

    judge_type = Column(String, default="standard") # standard, special
    judge_script = Column(String, nullable=True)


class TestCase(Base):
    __tablename__ = "test_case"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problem.id"), nullable=False)
    
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=False)
    
    is_sample = Column(Boolean, default=False)
    score = Column(Integer, default=100)
    order = Column(Integer, default=0)

    problem = relationship("Problem", back_populates="test_cases")