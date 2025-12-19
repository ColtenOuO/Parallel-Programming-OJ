import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base

class SubmissionStatus(str, enum.Enum):
    PENDING = "Pending"
    JUDGING = "Judging"
    AC = "Accepted"
    WA = "Wrong Answer"
    TLE = "Time Limit Exceeded"
    CE = "Compilation Error"
    ERR = "System Error"

class Submission(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problem.id"), nullable=False)
    
    code = Column(Text, nullable=False)
    language = Column(String, default="CPP")

    status = Column(String, default=SubmissionStatus.PENDING)
    result_details = Column(Text,nullable=True)

    submit_time = Column(DateTime, default=datetime.utcnow)
    execute_time = Column(String, nullable=True)
    memory_usage = Column(String, nullable=True)
    
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")