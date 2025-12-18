import uuid
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Problem(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    time_limit = Column(Integer, nullable=False)
    memory_limit = Column(Integer, nullable=False)
    core_number = Column(Integer, nullable=False)
    compile_command = Column(String, nullable=False)
    run_command = Column(String, nullable=False)
    input_file = Column(String, nullable=False)
    output_file = Column(String, nullable=False)
    